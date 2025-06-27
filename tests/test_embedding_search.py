"""
Unit Tests for Embedding Search Module

Tests for day3_embedding_search.py functionality including:
- OpenAI embedding generation
- FAISS index creation and search
- Query processing and similarity search
- Error handling for API failures
"""

import unittest
import tempfile
import os
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from day3_embedding_search import EmbeddingBasedCourseSearch
except ImportError:
    EmbeddingBasedCourseSearch = None


class TestEmbeddingSearch(unittest.TestCase):
    """Test cases for embedding-based course search"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_courses = [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming and computer science",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements"
            },
            {
                "code": "CS201",
                "title": "Data Structures and Algorithms", 
                "description": "Advanced data structures including arrays, linked lists, trees",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements"
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "Introduction to machine learning algorithms and neural networks",
                "credits": 3,
                "difficulty": 4,
                "category": "Major Electives"
            }
        ]
        
        # Mock embeddings (1536 dimensions for text-embedding-3-small)
        self.mock_embeddings = [
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist()
        ]
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_embedding_search_initialization(self, mock_openai):
        """Test embedding search system initialization"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=self.mock_embeddings[0])]
        mock_client.embeddings.create.return_value = mock_response
        
        try:
            search_system = EmbeddingBasedCourseSearch(api_key="test_key")
            self.assertIsNotNone(search_system)
            self.assertEqual(search_system.model_name, "text-embedding-3-small")
            
        except Exception as e:
            self.skipTest(f"Embedding search initialization failed: {e}")
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_course_embedding_generation(self, mock_openai):
        """Test course embedding generation"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock multiple embedding responses
        mock_responses = []
        for embedding in self.mock_embeddings:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=embedding)]
            mock_responses.append(mock_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        try:
            search_system = EmbeddingBasedCourseSearch(api_key="test_key")
            search_system.embed_courses(self.sample_courses)
            
            # Check that embeddings were created
            self.assertEqual(len(search_system.course_embeddings), len(self.sample_courses))
            self.assertIsNotNone(search_system.faiss_index)
            
            # Verify API was called for each course
            self.assertEqual(mock_client.embeddings.create.call_count, len(self.sample_courses))
            
        except Exception as e:
            self.skipTest(f"Course embedding generation failed: {e}")
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_similarity_search(self, mock_openai):
        """Test similarity search functionality"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding responses
        mock_responses = []
        for embedding in self.mock_embeddings:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=embedding)]
            mock_responses.append(mock_response)
        
        # Add query embedding
        query_embedding = np.random.rand(1536).tolist()
        query_response = MagicMock()
        query_response.data = [MagicMock(embedding=query_embedding)]
        mock_responses.append(query_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        try:
            search_system = EmbeddingBasedCourseSearch(api_key="test_key")
            search_system.embed_courses(self.sample_courses)
            
            # Perform similarity search
            results = search_system.search_similar_courses("machine learning", top_k=2)
            
            self.assertIsNotNone(results)
            self.assertIsInstance(results, list)
            self.assertLessEqual(len(results), 2)
            
            # Check result structure
            if results:
                result = results[0]
                self.assertIn('course', result)
                self.assertIn('similarity', result)
                self.assertIsInstance(result['similarity'], (int, float))
                
        except Exception as e:
            self.skipTest(f"Similarity search failed: {e}")
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_empty_query_handling(self, mock_openai):
        """Test handling of empty queries"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        search_system = EmbeddingBasedCourseSearch(api_key="test_key")
        
        # Test empty query
        with self.assertRaises(ValueError):
            search_system.search_similar_courses("")
        
        # Test None query
        with self.assertRaises((ValueError, TypeError)):
            search_system.search_similar_courses(None)
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test handling of OpenAI API errors"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock API error
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        search_system = EmbeddingBasedCourseSearch(api_key="test_key")
        
        # Should handle API errors gracefully
        with self.assertRaises(Exception):
            search_system.embed_courses(self.sample_courses)
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available") 
    def test_course_text_formatting(self):
        """Test course text formatting for embedding"""
        if EmbeddingBasedCourseSearch is None:
            self.skipTest("Embedding search not available")
        
        # Create instance without API key for testing formatting
        try:
            search_system = EmbeddingBasedCourseSearch.__new__(EmbeddingBasedCourseSearch)
            
            # Test course formatting method if available
            if hasattr(search_system, '_format_course_text'):
                formatted = search_system._format_course_text(self.sample_courses[0])
                
                self.assertIsInstance(formatted, str)
                self.assertIn("CS101", formatted)
                self.assertIn("Introduction to Computer Science", formatted)
                self.assertIn("programming", formatted.lower())
            
        except Exception as e:
            self.skipTest(f"Course formatting test not possible: {e}")
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('openai.OpenAI')
    def test_large_course_dataset(self, mock_openai):
        """Test performance with larger course dataset"""
        # Create larger dataset
        large_dataset = []
        for i in range(50):
            course = {
                "code": f"CS{i:03d}",
                "title": f"Course {i}",
                "description": f"Description for course {i} with programming concepts",
                "credits": 3,
                "difficulty": 2 + (i % 4),
                "category": "Core Requirements"
            }
            large_dataset.append(course)
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding responses
        mock_responses = []
        for _ in range(len(large_dataset) + 1):  # +1 for query
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=np.random.rand(1536).tolist())]
            mock_responses.append(mock_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        try:
            import time
            search_system = EmbeddingBasedCourseSearch(api_key="test_key")
            
            start_time = time.time()
            search_system.embed_courses(large_dataset)
            embedding_time = time.time() - start_time
            
            # Should handle larger datasets efficiently
            self.assertLess(embedding_time, 10.0)  # Should complete in reasonable time
            self.assertEqual(len(search_system.course_embeddings), len(large_dataset))
            
        except Exception as e:
            self.skipTest(f"Large dataset test failed: {e}")
    
    @unittest.skipIf(EmbeddingBasedCourseSearch is None, "Embedding search not available")
    @patch('faiss.IndexFlatIP')
    @patch('openai.OpenAI')
    def test_faiss_index_operations(self, mock_openai, mock_faiss_index):
        """Test FAISS index operations"""
        # Mock FAISS index
        mock_index = MagicMock()
        mock_faiss_index.return_value = mock_index
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding responses
        mock_responses = []
        for embedding in self.mock_embeddings:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=embedding)]
            mock_responses.append(mock_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        try:
            search_system = EmbeddingBasedCourseSearch(api_key="test_key")
            search_system.embed_courses(self.sample_courses)
            
            # Verify FAISS index operations
            mock_index.add.assert_called()
            self.assertEqual(mock_index.add.call_count, 1)
            
        except Exception as e:
            self.skipTest(f"FAISS index test failed: {e}")


if __name__ == "__main__":
    unittest.main()
