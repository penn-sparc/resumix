"""
Resume Embedding Store using FAISS for efficient similarity search and caching.
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


class ResumeEmbeddingStore:
    """
    FAISS-based storage and retrieval system for resume embeddings.
    
    This class provides efficient storage and similarity search for resumes
    using FAISS (Facebook AI Similarity Search) with caching capabilities.
    Includes user-based resume counting and analytics.
    """
    
    def __init__(self, embedding_dim: int = 384, index_file: str = "resume_embeddings.faiss"):
        """
        Initialize the ResumeEmbeddingStore.
        
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
        self.resume_metadata = {}
        
        # Resume counting and tracking
        self.resume_count = 0
        self.last_added_timestamp = None
        
        # Get sentence transformer instance
        self.sentence_transformer = SentenceTransformerUtils.get_instance()
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"ResumeEmbeddingStore initialized with {self.get_resume_count()} resumes")
    
    def add_resume(self, resume_id: str, resume_text: str, sections: Dict, user_id: str = None) -> bool:
        """
        Add resume with embeddings to FAISS index.
        
        Args:
            resume_id: Unique identifier for the resume
            resume_text: Full resume text
            sections: Parsed resume sections
            user_id: Optional user identifier
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            # Check if resume already exists
            if resume_id in self.resume_metadata:
                logger.warning(f"Resume {resume_id} already exists in index")
                return False
            
            # Generate embedding for the resume
            embedding = self.sentence_transformer.encode(resume_text, convert_to_tensor=False)
            
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            embedding = embedding.reshape(1, -1).astype(np.float32)
            
            # Add to FAISS index
            faiss_index = self.index.ntotal
            self.index.add(embedding)
            
            # Store metadata
            self.resume_metadata[resume_id] = {
                'faiss_index': faiss_index,
                'resume_text': resume_text,
                'sections': sections,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'embedding_version': 'paraphrase-multilingual-MiniLM-L12-v2'
            }
            
            # Update counters
            self.resume_count = self.index.ntotal
            self.last_added_timestamp = datetime.now().isoformat()
            
            logger.info(f"Successfully added resume {resume_id} to index (total: {self.get_resume_count()})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding resume {resume_id} to index: {e}")
            return False
    
    def get_resume_count(self) -> int:
        """Return total number of resumes in index."""
        return self.index.ntotal
    
    def get_resume_count_by_user(self, user_id: str) -> int:
        """
        Return number of resumes for specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            int: Number of resumes for the user
        """
        count = 0
        for metadata in self.resume_metadata.values():
            if metadata.get('user_id') == user_id:
                count += 1
        return count
    
    def search_similar_resumes(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find k most similar resumes.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of similar resumes to return
            
        Returns:
            List of (resume_id, similarity_score) tuples
        """
        if self.get_resume_count() == 0:
            logger.warning("No resumes in index for similarity search")
            return []
        
        try:
            # Ensure query is properly formatted
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Normalize query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.astype(np.float32)
            
            # Search in FAISS index
            k = min(k, self.get_resume_count())
            similarities, indices = self.index.search(query_embedding, k)
            
            # Map indices back to resume IDs
            results = []
            for i, (similarity, faiss_idx) in enumerate(zip(similarities[0], indices[0])):
                if faiss_idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                    
                # Find resume_id by faiss_index
                resume_id = None
                for rid, metadata in self.resume_metadata.items():
                    if metadata['faiss_index'] == faiss_idx:
                        resume_id = rid
                        break
                
                if resume_id:
                    results.append((resume_id, float(similarity)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar resumes: {e}")
            return []
    
    def get_resume_embedding(self, resume_id: str) -> Optional[np.ndarray]:
        """
        Retrieve cached embedding for a resume.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            Embedding vector or None if not found
        """
        if resume_id not in self.resume_metadata:
            return None
        
        try:
            faiss_idx = self.resume_metadata[resume_id]['faiss_index']
            
            # Get embedding from FAISS index
            embedding = self.index.reconstruct(faiss_idx)
            return embedding
            
        except Exception as e:
            logger.error(f"Error retrieving embedding for resume {resume_id}: {e}")
            return None
    
    def remove_resume(self, resume_id: str) -> bool:
        """
        Remove resume from index.
        
        Args:
            resume_id: Resume identifier to remove
            
        Returns:
            bool: True if successfully removed
        """
        if resume_id not in self.resume_metadata:
            logger.warning(f"Resume {resume_id} not found in index")
            return False
        
        try:
            # Remove from metadata
            del self.resume_metadata[resume_id]
            
            # Note: FAISS doesn't support individual removal, so we need to rebuild
            # the index without the removed resume
            self._rebuild_index()
            
            # Update counters
            self.resume_count = self.index.ntotal
            
            logger.info(f"Successfully removed resume {resume_id} from index")
            return True
            
        except Exception as e:
            logger.error(f"Error removing resume {resume_id}: {e}")
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
                pickle.dump(self.resume_metadata, f)
            
            logger.info(f"Successfully saved index with {self.get_resume_count()} resumes")
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
                    self.resume_metadata = pickle.load(f)
                
                # Update counters
                self.resume_count = self.index.ntotal
                if self.resume_metadata:
                    # Find the latest timestamp
                    latest_time = max(
                        metadata.get('created_at', '')
                        for metadata in self.resume_metadata.values()
                    )
                    self.last_added_timestamp = latest_time
                
                logger.info(f"Successfully loaded index with {self.get_resume_count()} resumes")
                return True
            else:
                logger.info("No existing index found, starting fresh")
                return False
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            # Reset to empty state on error
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.resume_metadata = {}
            self.resume_count = 0
            self.last_added_timestamp = None
            return False
    
    def _rebuild_index(self):
        """Rebuild the FAISS index from current metadata."""
        try:
            # Create new index
            new_index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Re-add all resumes
            for resume_id, metadata in self.resume_metadata.items():
                # Re-generate embedding from text
                embedding = self.sentence_transformer.encode(
                    metadata['resume_text'], convert_to_tensor=False
                )
                embedding = embedding / np.linalg.norm(embedding)
                embedding = embedding.reshape(1, -1).astype(np.float32)
                
                # Update faiss_index in metadata
                metadata['faiss_index'] = new_index.ntotal
                new_index.add(embedding)
            
            # Replace old index
            self.index = new_index
            
            logger.info(f"Successfully rebuilt index with {self.get_resume_count()} resumes")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Return comprehensive index statistics.
        
        Returns:
            Dictionary containing index statistics
        """
        return {
            'total_resumes': self.get_resume_count(),
            'index_size_mb': self._get_index_size(),
            'last_added': self.last_added_timestamp,
            'embedding_dim': self.embedding_dim,
            'users_with_resumes': len(set(
                m.get('user_id') for m in self.resume_metadata.values() 
                if m.get('user_id')
            )),
            'avg_resumes_per_user': self._calculate_avg_resumes_per_user(),
            'index_file': str(self.index_file),
            'metadata_file': str(self.metadata_file)
        }
    
    def get_resume_distribution(self) -> Dict[str, int]:
        """
        Return resume count distribution by user.
        
        Returns:
            Dictionary mapping user_id to resume count
        """
        distribution = {}
        for metadata in self.resume_metadata.values():
            user_id = metadata.get('user_id', 'unknown')
            distribution[user_id] = distribution.get(user_id, 0) + 1
        return distribution
    
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
    
    def _calculate_avg_resumes_per_user(self) -> float:
        """Calculate average resumes per user."""
        try:
            users = set(
                m.get('user_id') for m in self.resume_metadata.values()
                if m.get('user_id')
            )
            if not users:
                return 0.0
            return round(self.get_resume_count() / len(users), 2)
        except Exception:
            return 0.0
    
    def get_resume_metadata(self, resume_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific resume.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            Resume metadata dictionary or None if not found
        """
        return self.resume_metadata.get(resume_id)
    
    def list_resumes_by_user(self, user_id: str) -> List[str]:
        """
        List all resume IDs for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of resume IDs for the user
        """
        return [
            resume_id for resume_id, metadata in self.resume_metadata.items()
            if metadata.get('user_id') == user_id
        ]
    
    def list_all_resumes(self) -> List[str]:
        """
        List all resume IDs in the index.
        
        Returns:
            List of resume IDs
        """
        return list(self.resume_metadata.keys())
    
    def clear_index(self) -> bool:
        """
        Clear all resumes from the index.
        
        Returns:
            bool: True if successfully cleared
        """
        try:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.resume_metadata = {}
            self.resume_count = 0
            self.last_added_timestamp = None
            
            # Remove files if they exist
            if self.index_file.exists():
                self.index_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            logger.info("Successfully cleared resume embedding index")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False
    
    def search_resumes_by_user(self, user_id: str, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find similar resumes for a specific user.
        
        Args:
            user_id: User identifier
            query_embedding: Query embedding vector
            k: Number of similar resumes to return
            
        Returns:
            List of (resume_id, similarity_score) tuples for the user
        """
        # Get all resumes for the user
        user_resumes = self.list_resumes_by_user(user_id)
        
        if not user_resumes:
            logger.warning(f"No resumes found for user {user_id}")
            return []
        
        # Search all resumes first
        all_similar = self.search_similar_resumes(query_embedding, k=self.get_resume_count())
        
        # Filter to only include user's resumes
        user_similar = [
            (resume_id, score) for resume_id, score in all_similar
            if resume_id in user_resumes
        ]
        
        # Return top k
        return user_similar[:k]
    
    def get_resume_sections(self, resume_id: str) -> Optional[Dict]:
        """
        Get parsed sections for a specific resume.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            Resume sections dictionary or None if not found
        """
        metadata = self.get_resume_metadata(resume_id)
        if metadata:
            return metadata.get('sections')
        return None