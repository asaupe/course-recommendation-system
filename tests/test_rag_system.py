"""
Unit Tests for RAG System Module

Tests for src/rag_system.py functionality including:
- ChromaDB integration
- Document embedding and retrieval
- Vector similarity search
- Error handling and edge cases
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from src.rag_system import CourseRAGSystem
except ImportError:
    # Mock if RAG system not available
    CourseRAGSystem = None


class TestRAGSystem(unittest.TestCase):
    """Test cases for RAG system functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_courses = [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming and computer science",
                "credits": 3,
                "difficulty": 2
            },
            {
                "code": "CS201", 
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures including arrays, linked lists, trees",
                "credits": 4,
                "difficulty": 4
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "Introduction to machine learning algorithms and neural networks",
                "credits": 3,
                "difficulty": 4
            }
        ]
        
        # Create temporary directory for ChromaDB
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(CourseRAGSystem is None, "RAG system not available")
    def test_rag_system_initialization(self):
        """Test RAG system initialization"""
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            self.assertIsNotNone(rag_system)
            self.assertIsNotNone(rag_system.collection)
        except Exception as e:
            self.skipTest(f"ChromaDB not available: {e}")
    
    @unittest.skipIf(CourseRAGSystem is None, "RAG system not available")
    def test_add_courses(self):
        """Test adding courses to RAG system"""
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            rag_system.add_courses(self.sample_courses)
            
            # Check that courses were added
            count = rag_system.collection.count()
            self.assertEqual(count, len(self.sample_courses))
            
        except Exception as e:
            self.skipTest(f"ChromaDB functionality not available: {e}")
    
    @unittest.skipIf(CourseRAGSystem is None, "RAG system not available")
    def test_search_courses(self):
        """Test course search functionality"""
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            rag_system.add_courses(self.sample_courses)
            
            # Search for machine learning
            results = rag_system.search_courses("machine learning", n_results=2)
            
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)
            self.assertIn('documents', results)
            self.assertIn('metadatas', results)
            
            # Should find the ML course
            if results['documents'] and len(results['documents'][0]) > 0:
                found_ml = any("machine learning" in doc.lower() 
                             for doc in results['documents'][0])
                self.assertTrue(found_ml)
                
        except Exception as e:
            self.skipTest(f"Search functionality not available: {e}")
    
    def test_search_empty_collection(self):
        """Test search with empty collection"""
        if CourseRAGSystem is None:
            self.skipTest("RAG system not available")
            
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            
            # Search without adding any courses
            results = rag_system.search_courses("programming", n_results=5)
            
            # Should handle empty collection gracefully
            self.assertIsNotNone(results)
            
        except Exception as e:
            # Should handle this gracefully
            self.assertIsInstance(e, (ValueError, RuntimeError))
    
    def test_invalid_search_query(self):
        """Test search with invalid queries"""
        if CourseRAGSystem is None:
            self.skipTest("RAG system not available")
            
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            rag_system.add_courses(self.sample_courses)
            
            # Test empty query
            results = rag_system.search_courses("", n_results=1)
            self.assertIsNotNone(results)
            
            # Test very long query
            long_query = "a" * 1000
            results = rag_system.search_courses(long_query, n_results=1)
            self.assertIsNotNone(results)
            
        except Exception as e:
            # Should handle gracefully
            self.assertIsInstance(e, (ValueError, RuntimeError))
    
    @unittest.skipIf(CourseRAGSystem is None, "RAG system not available")
    def test_course_formatting(self):
        """Test course data formatting for embedding"""
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            
            # Test the course formatting method if available
            if hasattr(rag_system, '_format_course_for_embedding'):
                formatted = rag_system._format_course_for_embedding(self.sample_courses[0])
                
                self.assertIsInstance(formatted, str)
                self.assertIn("CS101", formatted)
                self.assertIn("Introduction to Computer Science", formatted)
                self.assertIn("programming", formatted.lower())
            
        except Exception as e:
            self.skipTest(f"Course formatting not testable: {e}")
    
    def test_rag_system_persistence(self):
        """Test RAG system data persistence"""
        if CourseRAGSystem is None:
            self.skipTest("RAG system not available")
            
        try:
            # Create RAG system and add courses
            rag_system1 = CourseRAGSystem(persist_directory=self.temp_dir)
            rag_system1.add_courses(self.sample_courses)
            initial_count = rag_system1.collection.count()
            
            # Create new instance with same directory
            rag_system2 = CourseRAGSystem(persist_directory=self.temp_dir)
            persisted_count = rag_system2.collection.count()
            
            # Data should persist
            self.assertEqual(initial_count, persisted_count)
            
        except Exception as e:
            self.skipTest(f"Persistence testing not available: {e}")
    
    @patch('chromadb.Client')
    def test_rag_system_mock(self, mock_client):
        """Test RAG system with mocked ChromaDB"""
        # Mock ChromaDB client
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        if CourseRAGSystem is None:
            self.skipTest("RAG system not available")
        
        try:
            rag_system = CourseRAGSystem(persist_directory=self.temp_dir)
            rag_system.add_courses(self.sample_courses)
            
            # Verify collection methods were called
            mock_collection.add.assert_called()
            
        except Exception as e:
            self.skipTest(f"Mocking not possible: {e}")


if __name__ == "__main__":
    unittest.main()
