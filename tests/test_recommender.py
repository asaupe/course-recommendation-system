"""
Unit tests for the Course Recommendation System
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from course_recommender import CourseRecommender
from data_manager import DataManager
from rag_system import RAGSystem
from prompt_templates import PromptTemplates


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_manager = DataManager(data_directory="test_data")
    
    def test_load_courses(self):
        """Test loading courses."""
        courses = self.data_manager.load_courses()
        self.assertIsInstance(courses, list)
        self.assertGreater(len(courses), 0)
    
    def test_search_courses(self):
        """Test course search functionality."""
        results = self.data_manager.search_courses("computer science")
        self.assertIsInstance(results, list)
    
    def test_get_course_by_code(self):
        """Test getting course by code."""
        # This will use sample data
        course = self.data_manager.get_course_by_code("CS101")
        if course:
            self.assertIn('code', course)
            self.assertIn('title', course)


class TestRAGSystem(unittest.TestCase):
    """Test cases for RAGSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rag_system = RAGSystem()
    
    def test_search_courses_fallback(self):
        """Test course search with fallback implementation."""
        results = self.rag_system.search_courses("programming", max_results=5)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
    
    def test_add_courses(self):
        """Test adding courses to RAG system."""
        sample_courses = [
            {
                "code": "TEST101",
                "title": "Test Course",
                "description": "A test course for unit testing",
                "credits": 3,
                "difficulty": 2,
                "category": "Test"
            }
        ]
        # Should not raise an exception
        self.rag_system.add_courses(sample_courses)


class TestPromptTemplates(unittest.TestCase):
    """Test cases for PromptTemplates class."""
    
    def test_system_prompt(self):
        """Test system prompt generation."""
        prompt = PromptTemplates.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_recommendation_prompt(self):
        """Test recommendation prompt generation."""
        user_profile = {
            'name': 'Test Student',
            'major': 'Computer Science',
            'interests': 'programming, AI',
            'required_categories': ['Core Requirements']
        }
        candidate_courses = [
            {
                'code': 'CS101',
                'title': 'Intro to CS',
                'description': 'Programming basics',
                'credits': 3,
                'difficulty': 2,
                'category': 'Core Requirements'
            }
        ]
        
        prompt = PromptTemplates.get_recommendation_prompt(user_profile, candidate_courses)
        self.assertIsInstance(prompt, str)
        self.assertIn('Test Student', prompt)
        self.assertIn('CS101', prompt)


class TestCourseRecommender(unittest.TestCase):
    """Test cases for CourseRecommender class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('src.course_recommender.OpenAI'):
                self.recommender = CourseRecommender()
    
    def test_initialization(self):
        """Test recommender initialization."""
        self.assertIsNotNone(self.recommender.rag_system)
        self.assertIsNotNone(self.recommender.prompt_templates)
        self.assertIsNotNone(self.recommender.data_manager)
    
    @patch('src.course_recommender.OpenAI')
    def test_get_sample_recommendations(self, mock_openai):
        """Test getting sample recommendations."""
        user_profile = {
            'name': 'Test Student',
            'major': 'Computer Science',
            'interests': 'programming',
            'required_categories': ['Core Requirements'],
            'difficulty_preference': 3
        }
        
        # Test fallback recommendations
        recommendations = self.recommender._get_sample_recommendations(user_profile)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIn('code', rec)
            self.assertIn('title', rec)
            self.assertIn('reason', rec)


if __name__ == '__main__':
    # Set up environment for testing
    os.environ['OPENAI_API_KEY'] = 'test_key_for_testing'
    
    # Run tests
    unittest.main()
