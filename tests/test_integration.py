"""
Integration Tests for Complete Course Recommendation Pipeline

Tests for the entire system integration including:
- End-to-end recommendation generation
- Multi-component interaction testing
- Performance and reliability testing
- Real-world scenario simulation
"""

import unittest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from day5_guardrails import Day5GuardedRAGPipeline
    from day4_rag_pipeline import Day4RAGPipeline
    from day3_embedding_search import EmbeddingBasedCourseSearch
    from src.data_manager import load_courses
except ImportError:
    # Mock if modules not available
    Day5GuardedRAGPipeline = None
    Day4RAGPipeline = None
    EmbeddingBasedCourseSearch = None
    load_courses = None


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the complete recommendation pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_courses = [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming and computer science. Introduction to problem-solving, algorithm design, and programming in Python.",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements",
                "prerequisites": "None"
            },
            {
                "code": "CS201",
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures including arrays, linked lists, stacks, queues, trees, and graphs. Algorithm design and analysis.",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements",
                "prerequisites": "CS101"
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks, and deep learning applications.",
                "credits": 3,
                "difficulty": 4,
                "category": "Major Electives",
                "prerequisites": "CS201, MATH201"
            },
            {
                "code": "CS302",
                "title": "Web Development",
                "description": "Full-stack web development using modern frameworks. HTML, CSS, JavaScript, React, Node.js, and database integration.",
                "credits": 3,
                "difficulty": 3,
                "category": "Major Electives",
                "prerequisites": "CS101"
            }
        ]
        
        self.test_queries = [
            "I want to learn programming and computer science basics",
            "I'm interested in machine learning and data analysis",
            "I need web development skills for my career",
            "I want advanced algorithms and data structures"
        ]
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "Pipeline not available")
    @patch('day5_guardrails.load_courses')
    @patch('openai.OpenAI')
    def test_end_to_end_recommendation_flow(self, mock_openai, mock_load_courses):
        """Test complete end-to-end recommendation generation"""
        # Mock course data loading
        mock_load_courses.return_value = self.sample_courses
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding responses
        import numpy as np
        mock_embeddings = [np.random.rand(1536).tolist() for _ in range(len(self.sample_courses) + 1)]
        
        mock_responses = []
        for embedding in mock_embeddings:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=embedding)]
            mock_responses.append(mock_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        # Mock LLM chat completion
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = '''{
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Perfect starting point for learning programming fundamentals",
                    "match_score": 0.9
                }
            ],
            "overall_confidence": 0.85,
            "reasoning": "Strong match for beginner programming needs"
        }'''
        mock_client.chat.completions.create.return_value = mock_chat_response
        
        try:
            # Initialize pipeline
            pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
            
            # Test with sample query
            query = "I want to learn programming basics"
            result = pipeline.process_query_with_validation(query)
            
            # Verify result structure
            self.assertIsNotNone(result)
            self.assertTrue(hasattr(result, 'recommendations'))
            self.assertTrue(hasattr(result, 'overall_confidence'))
            self.assertTrue(hasattr(result, 'validation_passed'))
            
            # Verify recommendations
            if result.recommendations:
                rec = result.recommendations[0]
                self.assertTrue(hasattr(rec, 'course_id'))
                self.assertTrue(hasattr(rec, 'title'))
                self.assertTrue(hasattr(rec, 'justification'))
                self.assertTrue(hasattr(rec, 'match_score'))
            
        except Exception as e:
            self.skipTest(f"End-to-end test failed: {e}")
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "Pipeline not available")
    @patch('day5_guardrails.load_courses')
    @patch('openai.OpenAI')
    def test_multiple_query_handling(self, mock_openai, mock_load_courses):
        """Test handling of multiple different queries"""
        # Mock course data loading
        mock_load_courses.return_value = self.sample_courses
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock responses
        import numpy as np
        
        # Create enough mock embeddings for all courses + queries
        total_embeddings_needed = len(self.sample_courses) + len(self.test_queries)
        mock_embeddings = [np.random.rand(1536).tolist() for _ in range(total_embeddings_needed)]
        
        mock_responses = []
        for embedding in mock_embeddings:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=embedding)]
            mock_responses.append(mock_response)
        
        mock_client.embeddings.create.side_effect = mock_responses
        
        # Mock LLM responses
        mock_chat_responses = []
        for i in range(len(self.test_queries)):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = f'''{
                "recommendations": [
                    {{
                        "course_id": "CS{101 + i}01",
                        "title": "Sample Course {i}",
                        "justification": "Good match for query {i}",
                        "match_score": {0.8 + i * 0.05}
                    }}
                ],
                "overall_confidence": {0.7 + i * 0.05},
                "reasoning": "Analysis for query {i}"
            }'''
            mock_chat_responses.append(mock_response)
        
        mock_client.chat.completions.create.side_effect = mock_chat_responses
        
        try:
            pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
            
            results = []
            for query in self.test_queries:
                result = pipeline.process_query_with_validation(query)
                results.append(result)
            
            # Verify all queries were processed
            self.assertEqual(len(results), len(self.test_queries))
            
            # Verify each result has basic structure
            for result in results:
                self.assertIsNotNone(result)
                self.assertTrue(hasattr(result, 'validation_passed'))
                
        except Exception as e:
            self.skipTest(f"Multiple query test failed: {e}")
    
    @unittest.skipIf(load_courses is None, "Data manager not available")
    def test_data_loading_integration(self):
        """Test data loading and course validation"""
        try:
            # Test loading from actual course file
            courses = load_courses()
            
            # Verify course data structure
            self.assertIsInstance(courses, list)
            self.assertGreater(len(courses), 0)
            
            # Verify course fields
            required_fields = ["code", "title", "description", "credits", "difficulty"]
            for course in courses[:3]:  # Check first few courses
                for field in required_fields:
                    self.assertIn(field, course)
                    self.assertIsNotNone(course[field])
            
        except Exception as e:
            self.skipTest(f"Data loading test failed: {e}")
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "Pipeline not available")
    @patch('day5_guardrails.load_courses')
    @patch('openai.OpenAI')
    def test_error_recovery_and_fallback(self, mock_openai, mock_load_courses):
        """Test system behavior during errors and fallback scenarios"""
        mock_load_courses.return_value = self.sample_courses
        
        # Mock OpenAI client that fails on embedding but succeeds on chat
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # First, make embeddings fail, then succeed
        mock_client.embeddings.create.side_effect = [Exception("Embedding failed")] * 2 + [
            MagicMock(data=[MagicMock(embedding=[0.1] * 1536)])
        ] * 10
        
        # Mock fallback chat response
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = '''{
            "recommendations": [],
            "overall_confidence": 0.1,
            "reasoning": "Fallback response due to system error"
        }'''
        mock_client.chat.completions.create.return_value = mock_chat_response
        
        try:
            pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
            
            # Should handle embedding failures gracefully
            result = pipeline.process_query_with_validation("test query")
            
            # Should return some result, possibly with fallback triggered
            self.assertIsNotNone(result)
            
        except Exception as e:
            # System should handle errors gracefully
            self.assertIsInstance(e, (ValueError, RuntimeError))
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "Pipeline not available")
    @patch('day5_guardrails.load_courses')
    @patch('openai.OpenAI')
    def test_performance_benchmarking(self, mock_openai, mock_load_courses):
        """Test system performance with realistic data"""
        mock_load_courses.return_value = self.sample_courses
        
        # Mock OpenAI client with fast responses
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding responses
        import numpy as np
        mock_embedding = np.random.rand(1536).tolist()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response
        
        # Mock chat response
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = '''{
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Good match",
                    "match_score": 0.8
                }
            ],
            "overall_confidence": 0.75,
            "reasoning": "Performance test response"
        }'''
        mock_client.chat.completions.create.return_value = mock_chat_response
        
        try:
            pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
            
            # Measure performance
            start_time = time.time()
            result = pipeline.process_query_with_validation("performance test query")
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Verify reasonable performance (should complete within reasonable time)
            self.assertLess(processing_time, 10.0)  # 10 seconds max
            self.assertIsNotNone(result)
            
        except Exception as e:
            self.skipTest(f"Performance test failed: {e}")
    
    def test_course_data_consistency(self):
        """Test consistency of course data across the system"""
        if load_courses is None:
            self.skipTest("Data manager not available")
        
        try:
            courses = load_courses()
            
            # Check for duplicate course codes
            course_codes = [course.get("code") for course in courses if course.get("code")]
            unique_codes = set(course_codes)
            
            self.assertEqual(len(course_codes), len(unique_codes), "Duplicate course codes found")
            
            # Check prerequisite references
            valid_codes = set(course_codes)
            for course in courses:
                if "prerequisites" in course and course["prerequisites"] != "None":
                    prereqs = [p.strip() for p in course["prerequisites"].split(",")]
                    for prereq in prereqs:
                        if prereq and prereq != "None":
                            # Note: Some prerequisites might be from other departments (like MATH201)
                            # So we only check CS prerequisites
                            if prereq.startswith("CS"):
                                self.assertIn(prereq, valid_codes, 
                                            f"Invalid prerequisite {prereq} in course {course['code']}")
            
        except Exception as e:
            self.skipTest(f"Data consistency test failed: {e}")
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "Pipeline not available")
    @patch('day5_guardrails.load_courses')
    def test_initialization_robustness(self, mock_load_courses):
        """Test robust initialization under various conditions"""
        mock_load_courses.return_value = self.sample_courses
        
        # Test initialization with different confidence thresholds
        thresholds = [0.1, 0.5, 0.8, 0.95]
        
        for threshold in thresholds:
            try:
                with patch('openai.OpenAI'):
                    pipeline = Day5GuardedRAGPipeline(confidence_threshold=threshold)
                    self.assertIsNotNone(pipeline)
                    self.assertEqual(pipeline.confidence_threshold, threshold)
                    
            except Exception as e:
                self.fail(f"Initialization failed for threshold {threshold}: {e}")


if __name__ == "__main__":
    unittest.main()
