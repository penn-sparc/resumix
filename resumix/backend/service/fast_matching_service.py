"""
Fast Matching Service using FAISS-based embedding stores for efficient job-resume matching.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from loguru import logger

from resumix.backend.service.job_embedding_store import JobEmbeddingStore
from resumix.backend.service.resume_embedding_store import ResumeEmbeddingStore
from resumix.shared.utils.sentence_transformer_utils import SentenceTransformerUtils


class FastMatchingService:
    """
    High-performance job-resume matching service using cached embeddings.
    
    This service provides fast similarity matching between jobs and resumes
    using pre-computed embeddings stored in FAISS indices.
    """
    
    def __init__(self):
        """Initialize the FastMatchingService with embedding stores."""
        self.job_store = JobEmbeddingStore()
        self.resume_store = ResumeEmbeddingStore()
        self.sentence_transformer = SentenceTransformerUtils.get_instance()
        
        logger.info(f"FastMatchingService initialized with {self.job_store.get_job_count()} jobs and {self.resume_store.get_resume_count()} resumes")
    
    def find_best_candidates(self, job_id: str, k: int = 10) -> List[Dict]:
        """
        Find best resume candidates for a job using cached embeddings.
        
        Args:
            job_id: Job identifier
            k: Number of top candidates to return
            
        Returns:
            List of candidate dictionaries with resume details and scores
        """
        if job_id not in self.job_store.job_metadata:
            logger.warning(f"Job {job_id} not found in job embedding store")
            return []
        
        if self.resume_store.get_resume_count() == 0:
            logger.warning("No resumes in resume embedding store")
            return []
        
        try:
            # Get job embedding
            job_embedding = self.job_store.get_job_embedding(job_id)
            if job_embedding is None:
                logger.error(f"Failed to retrieve embedding for job {job_id}")
                return []
            
            # Find similar resumes
            similar_resumes = self.resume_store.search_similar_resumes(job_embedding, k=k)
            
            # Build candidate list with detailed information
            candidates = []
            for resume_id, similarity_score in similar_resumes:
                resume_metadata = self.resume_store.get_resume_metadata(resume_id)
                if resume_metadata:
                    candidate = {
                        'resume_id': resume_id,
                        'user_id': resume_metadata.get('user_id'),
                        'similarity_score': similarity_score,
                        'sections': resume_metadata.get('sections', {}),
                        'created_at': resume_metadata.get('created_at'),
                        'match_details': self._generate_match_details(
                            job_id, resume_id, similarity_score
                        )
                    }
                    candidates.append(candidate)
            
            logger.info(f"Found {len(candidates)} candidates for job {job_id}")
            return candidates
            
        except Exception as e:
            logger.error(f"Error finding candidates for job {job_id}: {e}")
            return []
    
    def find_best_jobs(self, resume_id: str, k: int = 10) -> List[Dict]:
        """
        Find best job matches for a resume using cached embeddings.
        
        Args:
            resume_id: Resume identifier
            k: Number of top job matches to return
            
        Returns:
            List of job dictionaries with details and scores
        """
        if resume_id not in self.resume_store.resume_metadata:
            logger.warning(f"Resume {resume_id} not found in resume embedding store")
            return []
        
        if self.job_store.get_job_count() == 0:
            logger.warning("No jobs in job embedding store")
            return []
        
        try:
            # Get resume embedding
            resume_embedding = self.resume_store.get_resume_embedding(resume_id)
            if resume_embedding is None:
                logger.error(f"Failed to retrieve embedding for resume {resume_id}")
                return []
            
            # Find similar jobs
            similar_jobs = self.job_store.search_similar_jobs(resume_embedding, k=k)
            
            # Build job list with detailed information
            jobs = []
            for job_id, similarity_score in similar_jobs:
                job_metadata = self.job_store.get_job_metadata(job_id)
                if job_metadata:
                    job = {
                        'job_id': job_id,
                        'similarity_score': similarity_score,
                        'structured_data': job_metadata.get('structured_data', {}),
                        'created_at': job_metadata.get('created_at'),
                        'match_details': self._generate_match_details(
                            job_id, resume_id, similarity_score
                        )
                    }
                    jobs.append(job)
            
            logger.info(f"Found {len(jobs)} job matches for resume {resume_id}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error finding jobs for resume {resume_id}: {e}")
            return []
    
    def batch_match_resumes(self, job_ids: List[str], resume_ids: List[str]) -> Dict[str, Any]:
        """
        Batch process multiple job-resume combinations.
        
        Args:
            job_ids: List of job identifiers
            resume_ids: List of resume identifiers
            
        Returns:
            Dictionary containing batch matching results
        """
        if not job_ids or not resume_ids:
            logger.warning("Empty job_ids or resume_ids provided for batch matching")
            return {'results': [], 'stats': {}}
        
        try:
            results = []
            processed_count = 0
            
            for job_id in job_ids:
                if job_id not in self.job_store.job_metadata:
                    logger.warning(f"Job {job_id} not found in job embedding store")
                    continue
                
                # Get job embedding
                job_embedding = self.job_store.get_job_embedding(job_id)
                if job_embedding is None:
                    continue
                
                # Find matches for this job among the specified resumes
                job_matches = []
                for resume_id in resume_ids:
                    if resume_id not in self.resume_store.resume_metadata:
                        continue
                    
                    # Get resume embedding
                    resume_embedding = self.resume_store.get_resume_embedding(resume_id)
                    if resume_embedding is None:
                        continue
                    
                    # Calculate similarity
                    similarity = self._calculate_similarity(job_embedding, resume_embedding)
                    
                    job_matches.append({
                        'resume_id': resume_id,
                        'similarity_score': float(similarity),
                        'user_id': self.resume_store.resume_metadata[resume_id].get('user_id')
                    })
                    processed_count += 1
                
                # Sort by similarity score
                job_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
                
                results.append({
                    'job_id': job_id,
                    'matches': job_matches,
                    'best_match': job_matches[0] if job_matches else None
                })
            
            stats = {
                'total_jobs_processed': len([r for r in results if r['matches']]),
                'total_comparisons': processed_count,
                'avg_matches_per_job': processed_count / len(job_ids) if job_ids else 0
            }
            
            logger.info(f"Batch processed {processed_count} job-resume comparisons")
            return {
                'results': results,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error in batch matching: {e}")
            return {'results': [], 'stats': {}}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Return system-wide statistics.
        
        Returns:
            Dictionary containing comprehensive system statistics
        """
        job_stats = self.job_store.get_index_stats()
        resume_stats = self.resume_store.get_index_stats()
        
        return {
            'job_stats': job_stats,
            'resume_stats': resume_stats,
            'total_possible_matches': job_stats['total_jobs'] * resume_stats['total_resumes'],
            'performance_metrics': {
                'embedding_model': 'paraphrase-multilingual-MiniLM-L12-v2',
                'embedding_dimension': 384,
                'similarity_metric': 'cosine'
            }
        }
    
    def find_similar_candidates(self, job_text: str, k: int = 10) -> List[Dict]:
        """
        Find similar resume candidates using raw job text (not cached).
        
        Args:
            job_text: Job description text
            k: Number of candidates to return
            
        Returns:
            List of candidate dictionaries
        """
        if self.resume_store.get_resume_count() == 0:
            logger.warning("No resumes in resume embedding store")
            return []
        
        try:
            # Generate embedding for job text
            job_embedding = self.sentence_transformer.encode(job_text, convert_to_tensor=False)
            job_embedding = job_embedding / np.linalg.norm(job_embedding)
            
            # Find similar resumes
            similar_resumes = self.resume_store.search_similar_resumes(job_embedding, k=k)
            
            # Build candidate list
            candidates = []
            for resume_id, similarity_score in similar_resumes:
                resume_metadata = self.resume_store.get_resume_metadata(resume_id)
                if resume_metadata:
                    candidate = {
                        'resume_id': resume_id,
                        'user_id': resume_metadata.get('user_id'),
                        'similarity_score': similarity_score,
                        'sections': resume_metadata.get('sections', {}),
                        'created_at': resume_metadata.get('created_at')
                    }
                    candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error finding candidates for job text: {e}")
            return []
    
    def find_similar_jobs(self, resume_text: str, k: int = 10) -> List[Dict]:
        """
        Find similar jobs using raw resume text (not cached).
        
        Args:
            resume_text: Resume text
            k: Number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        if self.job_store.get_job_count() == 0:
            logger.warning("No jobs in job embedding store")
            return []
        
        try:
            # Generate embedding for resume text
            resume_embedding = self.sentence_transformer.encode(resume_text, convert_to_tensor=False)
            resume_embedding = resume_embedding / np.linalg.norm(resume_embedding)
            
            # Find similar jobs
            similar_jobs = self.job_store.search_similar_jobs(resume_embedding, k=k)
            
            # Build job list
            jobs = []
            for job_id, similarity_score in similar_jobs:
                job_metadata = self.job_store.get_job_metadata(job_id)
                if job_metadata:
                    job = {
                        'job_id': job_id,
                        'similarity_score': similarity_score,
                        'structured_data': job_metadata.get('structured_data', {}),
                        'created_at': job_metadata.get('created_at')
                    }
                    jobs.append(job)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error finding jobs for resume text: {e}")
            return []
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        try:
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1_norm, embedding2_norm)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _generate_match_details(self, job_id: str, resume_id: str, similarity_score: float) -> Dict:
        """
        Generate detailed match information.
        
        Args:
            job_id: Job identifier
            resume_id: Resume identifier
            similarity_score: Similarity score
            
        Returns:
            Dictionary containing match details
        """
        return {
            'job_id': job_id,
            'resume_id': resume_id,
            'similarity_score': similarity_score,
            'match_quality': self._classify_match_quality(similarity_score),
            'computed_at': self._get_current_timestamp()
        }
    
    def _classify_match_quality(self, score: float) -> str:
        """
        Classify match quality based on similarity score.
        
        Args:
            score: Similarity score
            
        Returns:
            Match quality classification
        """
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'good'
        elif score >= 0.7:
            return 'fair'
        elif score >= 0.6:
            return 'poor'
        else:
            return 'very_poor'
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_match_statistics(self, job_id: str, resume_id: str) -> Optional[Dict]:
        """
        Get detailed statistics for a specific job-resume match.
        
        Args:
            job_id: Job identifier
            resume_id: Resume identifier
            
        Returns:
            Match statistics dictionary or None if not found
        """
        if job_id not in self.job_store.job_metadata:
            return None
        if resume_id not in self.resume_store.resume_metadata:
            return None
        
        try:
            job_embedding = self.job_store.get_job_embedding(job_id)
            resume_embedding = self.resume_store.get_resume_embedding(resume_id)
            
            if job_embedding is None or resume_embedding is None:
                return None
            
            similarity = self._calculate_similarity(job_embedding, resume_embedding)
            
            return {
                'job_id': job_id,
                'resume_id': resume_id,
                'similarity_score': similarity,
                'match_quality': self._classify_match_quality(similarity),
                'job_metadata': self.job_store.get_job_metadata(job_id),
                'resume_metadata': self.resume_store.get_resume_metadata(resume_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting match statistics: {e}")
            return None