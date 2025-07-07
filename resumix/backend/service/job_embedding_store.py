"""
Job Embedding Store using FAISS for efficient similarity search and caching.
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import numpy as np
import faiss
from loguru import logger

from resumix.shared.utils.sentence_transformer_utils import SentenceTransformerUtils


class JobEmbeddingStore:
    """
    FAISS-based storage and retrieval system for job description embeddings.
    
    This class provides efficient storage and similarity search for job descriptions
    using FAISS (Facebook AI Similarity Search) with caching capabilities.
    """
    
    def __init__(self, embedding_dim: int = 384, index_file: str = "job_embeddings.faiss"):
        """
        Initialize the JobEmbeddingStore.
        
        Args:
            embedding_dim: Dimension of the embedding vectors (default: 384 for MiniLM)
            index_file: Name of the FAISS index file to store/load
        """
        self.embedding_dim = embedding_dim
        self.base_dir = Path(__file__).parent.parent / "embeddings"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.base_dir / index_file
        self.metadata_file = self.base_dir / (Path(index_file).stem + "_metadata.pkl")
        
        # Initialize FAISS index with Inner Product (cosine similarity)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.job_metadata = {}
        
        # Get sentence transformer instance
        self.sentence_transformer = SentenceTransformerUtils.get_instance()
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"JobEmbeddingStore initialized with {self.get_job_count()} jobs")
    
    def add_job_description(self, job_id: str, jd_text: str, structured_data: Dict) -> bool:
        """
        Add job description with embeddings to FAISS index.
        
        Args:
            job_id: Unique identifier for the job
            jd_text: Full job description text
            structured_data: Parsed job description sections
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            # Check if job already exists
            if job_id in self.job_metadata:
                logger.warning(f"Job {job_id} already exists in index")
                return False
            
            # Generate embedding for the job description
            embedding = self.sentence_transformer.encode(jd_text, convert_to_tensor=False)
            
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            embedding = embedding.reshape(1, -1).astype(np.float32)
            
            # Add to FAISS index
            faiss_index = self.index.ntotal
            self.index.add(embedding)
            
            # Store metadata
            self.job_metadata[job_id] = {
                'faiss_index': faiss_index,
                'jd_text': jd_text,
                'structured_data': structured_data,
                'created_at': datetime.now().isoformat(),
                'embedding_version': 'paraphrase-multilingual-MiniLM-L12-v2'
            }
            
            logger.info(f"Successfully added job {job_id} to index (total: {self.get_job_count()})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding job {job_id} to index: {e}")
            return False
    
    def get_job_count(self) -> int:
        """Return total number of jobs in index."""
        return self.index.ntotal
    
    def search_similar_jobs(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find similar jobs to query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of similar jobs to return
            
        Returns:
            List of (job_id, similarity_score) tuples
        """
        if self.get_job_count() == 0:
            logger.warning("No jobs in index for similarity search")
            return []
        
        try:
            # Ensure query is properly formatted
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Normalize query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.astype(np.float32)
            
            # Search in FAISS index
            k = min(k, self.get_job_count())
            similarities, indices = self.index.search(query_embedding, k)
            
            # Map indices back to job IDs
            results = []
            for i, (similarity, faiss_idx) in enumerate(zip(similarities[0], indices[0])):
                if faiss_idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                    
                # Find job_id by faiss_index
                job_id = None
                for jid, metadata in self.job_metadata.items():
                    if metadata['faiss_index'] == faiss_idx:
                        job_id = jid
                        break
                
                if job_id:
                    results.append((job_id, float(similarity)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar jobs: {e}")
            return []
    
    def get_job_embedding(self, job_id: str) -> Optional[np.ndarray]:
        """
        Retrieve cached embedding for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Embedding vector or None if not found
        """
        if job_id not in self.job_metadata:
            return None
        
        try:
            faiss_idx = self.job_metadata[job_id]['faiss_index']
            
            # Get embedding from FAISS index
            embedding = self.index.reconstruct(faiss_idx)
            return embedding
            
        except Exception as e:
            logger.error(f"Error retrieving embedding for job {job_id}: {e}")
            return None
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove job from index (requires rebuild).
        
        Args:
            job_id: Job identifier to remove
            
        Returns:
            bool: True if successfully removed
        """
        if job_id not in self.job_metadata:
            logger.warning(f"Job {job_id} not found in index")
            return False
        
        try:
            # Remove from metadata
            del self.job_metadata[job_id]
            
            # Note: FAISS doesn't support individual removal, so we need to rebuild
            # the index without the removed job
            self._rebuild_index()
            
            logger.info(f"Successfully removed job {job_id} from index")
            return True
            
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False
    
    def save_index(self) -> bool:
        """
        Persist index and metadata to disk.
        
        Returns:
            bool: True if successfully saved
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.job_metadata, f)
            
            logger.info(f"Successfully saved index with {self.get_job_count()} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False
    
    def _load_index(self) -> bool:
        """
        Load existing index from disk.
        
        Returns:
            bool: True if successfully loaded
        """
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.job_metadata = pickle.load(f)
                
                logger.info(f"Successfully loaded index with {self.get_job_count()} jobs")
                return True
            else:
                logger.info("No existing index found, starting fresh")
                return False
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            # Reset to empty state on error
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.job_metadata = {}
            return False
    
    def _rebuild_index(self):
        """Rebuild the FAISS index from current metadata."""
        try:
            # Create new index
            new_index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Re-add all jobs
            for job_id, metadata in self.job_metadata.items():
                # Re-generate embedding from text
                embedding = self.sentence_transformer.encode(
                    metadata['jd_text'], convert_to_tensor=False
                )
                embedding = embedding / np.linalg.norm(embedding)
                embedding = embedding.reshape(1, -1).astype(np.float32)
                
                # Update faiss_index in metadata
                metadata['faiss_index'] = new_index.ntotal
                new_index.add(embedding)
            
            # Replace old index
            self.index = new_index
            
            logger.info(f"Successfully rebuilt index with {self.get_job_count()} jobs")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Return index statistics.
        
        Returns:
            Dictionary containing index statistics
        """
        return {
            'total_jobs': self.get_job_count(),
            'index_size_mb': self._get_index_size(),
            'last_updated': self._get_last_updated(),
            'embedding_dim': self.embedding_dim,
            'index_file': str(self.index_file),
            'metadata_file': str(self.metadata_file)
        }
    
    def _get_index_size(self) -> float:
        """Calculate index size in MB."""
        try:
            if self.index_file.exists():
                size_bytes = self.index_file.stat().st_size
                if self.metadata_file.exists():
                    size_bytes += self.metadata_file.stat().st_size
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _get_last_updated(self) -> Optional[str]:
        """Get last updated timestamp."""
        try:
            if self.index_file.exists():
                mtime = self.index_file.stat().st_mtime
                return datetime.fromtimestamp(mtime).isoformat()
            return None
        except Exception:
            return None
    
    def get_job_metadata(self, job_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job metadata dictionary or None if not found
        """
        return self.job_metadata.get(job_id)
    
    def list_all_jobs(self) -> List[str]:
        """
        List all job IDs in the index.
        
        Returns:
            List of job IDs
        """
        return list(self.job_metadata.keys())
    
    def clear_index(self) -> bool:
        """
        Clear all jobs from the index.
        
        Returns:
            bool: True if successfully cleared
        """
        try:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.job_metadata = {}
            
            # Remove files if they exist
            if self.index_file.exists():
                self.index_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            logger.info("Successfully cleared job embedding index")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False