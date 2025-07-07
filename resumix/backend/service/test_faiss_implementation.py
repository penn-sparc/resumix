"""
Unit tests for FAISS embedding store implementation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from resumix.backend.service.job_embedding_store import JobEmbeddingStore
from resumix.backend.service.resume_embedding_store import ResumeEmbeddingStore
from resumix.backend.service.fast_matching_service import FastMatchingService


class TestJobEmbeddingStore(unittest.TestCase):
    
    def setUp(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.job_store = JobEmbeddingStore(
            index_file=str(Path(self.temp_dir) / "test_job_embeddings.faiss")
        )
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_job_description(self):
        """Test adding job description to FAISS index."""
        job_id = "test_job_1"
        jd_text = "Software Engineer position requiring Python and machine learning skills."
        structured_data = {"overview": "Software Engineer", "requirements": "Python, ML"}
        
        success = self.job_store.add_job_description(job_id, jd_text, structured_data)
        self.assertTrue(success)
        self.assertEqual(self.job_store.get_job_count(), 1)
    
    def test_get_job_count(self):
        """Test resume counting functionality."""
        self.assertEqual(self.job_store.get_job_count(), 0)
        
        # Add a job
        self.job_store.add_job_description(
            "job1", "Test job description", {"overview": "Test"}
        )
        self.assertEqual(self.job_store.get_job_count(), 1)
    
    def test_search_similar_jobs(self):
        """Test similarity search."""
        # Add multiple jobs
        jobs = [
            ("job1", "Python developer position with machine learning focus"),
            ("job2", "Java developer role for enterprise applications"),
            ("job3", "Data scientist position using Python and TensorFlow")
        ]
        
        for job_id, jd_text in jobs:
            self.job_store.add_job_description(job_id, jd_text, {"overview": jd_text})
        
        # Create query embedding for Python/ML related job
        query_text = "Python machine learning engineer"
        query_embedding = self.job_store.sentence_transformer.encode(query_text)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search for similar jobs
        similar_jobs = self.job_store.search_similar_jobs(query_embedding, k=2)
        
        self.assertEqual(len(similar_jobs), 2)
        # job1 and job3 should be more similar than job2
        job_ids = [job_id for job_id, _ in similar_jobs]
        self.assertIn("job1", job_ids)
        self.assertIn("job3", job_ids)


class TestResumeEmbeddingStore(unittest.TestCase):
    
    def setUp(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.resume_store = ResumeEmbeddingStore(
            index_file=str(Path(self.temp_dir) / "test_resume_embeddings.faiss")
        )
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_resume(self):
        """Test adding resume to FAISS index."""
        resume_id = "test_resume_1"
        resume_text = "Experienced Python developer with 5 years in machine learning."
        sections = {"experience": "5 years Python", "skills": "ML, Python"}
        user_id = "user_123"
        
        success = self.resume_store.add_resume(resume_id, resume_text, sections, user_id)
        self.assertTrue(success)
        self.assertEqual(self.resume_store.get_resume_count(), 1)
        self.assertEqual(self.resume_store.get_resume_count_by_user(user_id), 1)
    
    def test_get_resume_count_by_user(self):
        """Test user-specific resume counting."""
        # Add resumes for different users
        self.resume_store.add_resume("r1", "Resume 1", {}, "user1")
        self.resume_store.add_resume("r2", "Resume 2", {}, "user1")
        self.resume_store.add_resume("r3", "Resume 3", {}, "user2")
        
        self.assertEqual(self.resume_store.get_resume_count_by_user("user1"), 2)
        self.assertEqual(self.resume_store.get_resume_count_by_user("user2"), 1)
        self.assertEqual(self.resume_store.get_resume_count_by_user("user3"), 0)
    
    def test_remove_resume(self):
        """Test resume removal and count updates."""
        # Add resume
        resume_id = "test_resume"
        self.resume_store.add_resume(resume_id, "Test resume", {}, "user1")
        self.assertEqual(self.resume_store.get_resume_count(), 1)
        
        # Remove resume
        success = self.resume_store.remove_resume(resume_id)
        self.assertTrue(success)
        self.assertEqual(self.resume_store.get_resume_count(), 0)


class TestFastMatchingService(unittest.TestCase):
    
    def setUp(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.matching_service = FastMatchingService()
        
        # Override with test stores
        self.matching_service.job_store = JobEmbeddingStore(
            index_file=str(Path(self.temp_dir) / "test_job_embeddings.faiss")
        )
        self.matching_service.resume_store = ResumeEmbeddingStore(
            index_file=str(Path(self.temp_dir) / "test_resume_embeddings.faiss")
        )
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)
    
    def test_find_best_candidates(self):
        """Test fast candidate matching."""
        # Add job
        job_id = "test_job"
        jd_text = "Python developer with machine learning experience"
        self.matching_service.job_store.add_job_description(
            job_id, jd_text, {"overview": jd_text}
        )
        
        # Add resumes
        resumes = [
            ("r1", "Python developer with 3 years ML experience", "user1"),
            ("r2", "Java developer with enterprise experience", "user2"),
            ("r3", "Data scientist using Python and TensorFlow", "user3")
        ]
        
        for resume_id, resume_text, user_id in resumes:
            self.matching_service.resume_store.add_resume(
                resume_id, resume_text, {"experience": resume_text}, user_id
            )
        
        # Find best candidates
        candidates = self.matching_service.find_best_candidates(job_id, k=2)
        
        self.assertEqual(len(candidates), 2)
        # Should find the most relevant candidates
        candidate_ids = [c['resume_id'] for c in candidates]
        self.assertIn("r1", candidate_ids)  # Python + ML experience
        self.assertIn("r3", candidate_ids)  # Data scientist with Python
    
    def test_batch_processing(self):
        """Test batch matching performance."""
        # Add jobs
        jobs = [
            ("job1", "Python developer position"),
            ("job2", "Java enterprise developer role")
        ]
        
        for job_id, jd_text in jobs:
            self.matching_service.job_store.add_job_description(
                job_id, jd_text, {"overview": jd_text}
            )
        
        # Add resumes
        resumes = [
            ("r1", "Python developer with experience", "user1"),
            ("r2", "Java enterprise developer", "user2")
        ]
        
        for resume_id, resume_text, user_id in resumes:
            self.matching_service.resume_store.add_resume(
                resume_id, resume_text, {"experience": resume_text}, user_id
            )
        
        # Batch process
        job_ids = ["job1", "job2"]
        resume_ids = ["r1", "r2"]
        
        results = self.matching_service.batch_match_resumes(job_ids, resume_ids)
        
        self.assertIn('results', results)
        self.assertIn('stats', results)
        self.assertEqual(len(results['results']), 2)


if __name__ == '__main__':
    unittest.main()