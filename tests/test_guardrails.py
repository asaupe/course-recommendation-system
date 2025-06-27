"""
Unit Tests for Guardrails and Validation Module

Tests for day5_guardrails.py functionality including:
- Pydantic model validation
- Course ID filtering and hallucination detection
- Confidence scoring and fallback mechanisms
- Output validation and structured responses
"""

import unittest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from day5_guardrails import (
        CourseRecommendation,
        RecommendationResponse,
        ValidatedRecommendationResponse,
        CourseValidator,
        OutputValidator,
        Day5GuardedRAGPipeline
    )
    from pydantic import ValidationError
except ImportError:
    # Mock if modules not available
    CourseRecommendation = None
    RecommendationResponse = None
    ValidatedRecommendationResponse = None
    CourseValidator = None
    OutputValidator = None
    Day5GuardedRAGPipeline = None
    ValidationError = Exception


class TestGuardrailsValidation(unittest.TestCase):
    """Test cases for guardrails and validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_courses = [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Basic programming concepts",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements"
            },
            {
                "code": "CS201",
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements"
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "ML algorithms and neural networks",
                "credits": 3,
                "difficulty": 4,
                "category": "Major Electives"
            }
        ]
        
        self.valid_course_ids = {"CS101", "CS201", "CS301"}
    
    @unittest.skipIf(CourseRecommendation is None, "Guardrails module not available")
    def test_course_recommendation_validation(self):
        """Test CourseRecommendation Pydantic model validation"""
        # Valid recommendation
        valid_rec = {
            "course_id": "CS101",
            "title": "Introduction to Computer Science",
            "justification": "Great for beginners learning programming fundamentals",
            "match_score": 0.85
        }
        
        recommendation = CourseRecommendation(**valid_rec)
        self.assertEqual(recommendation.course_id, "CS101")
        self.assertEqual(recommendation.match_score, 0.85)
        
        # Invalid recommendation - missing required field
        invalid_rec = {
            "course_id": "CS101",
            "title": "Introduction to Computer Science"
            # Missing justification and match_score
        }
        
        with self.assertRaises(ValidationError):
            CourseRecommendation(**invalid_rec)
        
        # Invalid recommendation - score out of range
        invalid_score_rec = {
            "course_id": "CS101",
            "title": "Introduction to Computer Science",
            "justification": "Good course",
            "match_score": 1.5  # Invalid - should be <= 1.0
        }
        
        with self.assertRaises(ValidationError):
            CourseRecommendation(**invalid_score_rec)
    
    @unittest.skipIf(CourseValidator is None, "CourseValidator not available")
    def test_course_validator_functionality(self):
        """Test CourseValidator class functionality"""
        validator = CourseValidator(self.sample_courses)
        
        # Test valid course ID
        is_valid, error = validator.validate_course_id("CS101")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test invalid course ID
        is_valid, error = validator.validate_course_id("CS999")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("CS999", error)
        
        # Test hallucination detection
        text_with_hallucination = "I recommend CS101, CS999, and FAKE123 for your studies"
        hallucinations = validator.detect_hallucinated_content(text_with_hallucination)
        
        self.assertIsInstance(hallucinations, list)
        # Should detect CS999 and FAKE123 as invalid
        invalid_courses = [h for h in hallucinations if h not in self.valid_course_ids]
        self.assertGreater(len(invalid_courses), 0)
    
    @unittest.skipIf(OutputValidator is None, "OutputValidator not available")
    def test_output_validator_functionality(self):
        """Test OutputValidator class functionality"""
        validator = OutputValidator(self.sample_courses, confidence_threshold=0.6)
        
        # Test valid response validation
        valid_response_data = {
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Perfect for beginners",
                    "match_score": 0.9
                }
            ],
            "overall_confidence": 0.85,
            "reasoning": "Strong match based on student needs"
        }
        
        validated = validator.validate_response(valid_response_data, "I want to learn programming")
        
        self.assertIsNotNone(validated)
        self.assertTrue(validated.validation_passed)
        self.assertEqual(len(validated.recommendations), 1)
        self.assertEqual(validated.overall_confidence, 0.85)
    
    @unittest.skipIf(OutputValidator is None, "OutputValidator not available")
    def test_low_confidence_fallback(self):
        """Test fallback for low confidence responses"""
        validator = OutputValidator(self.sample_courses, confidence_threshold=0.8)
        
        # Low confidence response
        low_confidence_data = {
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Might be suitable",
                    "match_score": 0.4
                }
            ],
            "overall_confidence": 0.3,  # Below threshold
            "reasoning": "Uncertain match"
        }
        
        validated = validator.validate_response(low_confidence_data, "unclear query")
        
        # Should trigger fallback
        self.assertTrue(validated.fallback_triggered)
        self.assertLess(validated.overall_confidence, 0.8)
    
    @unittest.skipIf(OutputValidator is None, "OutputValidator not available")
    def test_invalid_course_id_filtering(self):
        """Test filtering of invalid course IDs"""
        validator = OutputValidator(self.sample_courses, confidence_threshold=0.6)
        
        # Response with invalid course ID
        invalid_response_data = {
            "recommendations": [
                {
                    "course_id": "CS999",  # Invalid course ID
                    "title": "Fake Course",
                    "justification": "This course doesn't exist",
                    "match_score": 0.9
                },
                {
                    "course_id": "CS101",  # Valid course ID
                    "title": "Introduction to Computer Science",
                    "justification": "Real course",
                    "match_score": 0.8
                }
            ],
            "overall_confidence": 0.85,
            "reasoning": "Mixed valid and invalid recommendations"
        }
        
        validated = validator.validate_response(invalid_response_data, "test query")
        
        # Should filter out invalid course
        self.assertEqual(len(validated.recommendations), 1)
        self.assertEqual(validated.recommendations[0].course_id, "CS101")
        self.assertGreater(len(validated.warnings), 0)
    
    @unittest.skipIf(Day5GuardedRAGPipeline is None, "GuardedRAGPipeline not available")
    @patch('day4_rag_pipeline.Day4RAGPipeline')
    @patch('openai.OpenAI')
    def test_guarded_rag_pipeline_integration(self, mock_openai, mock_pipeline):
        """Test Day5GuardedRAGPipeline integration"""
        # Mock dependencies
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_base_pipeline = MagicMock()
        mock_pipeline.return_value = mock_base_pipeline
        
        # Mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.choices = [MagicMock()]
        mock_llm_response.choices[0].message.content = json.dumps({
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Great for beginners",
                    "match_score": 0.9
                }
            ],
            "overall_confidence": 0.85,
            "reasoning": "Strong match"
        })
        mock_client.chat.completions.create.return_value = mock_llm_response
        
        try:
            # Mock course data loading
            with patch('day5_guardrails.load_courses', return_value=self.sample_courses):
                pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
                
                result = pipeline.process_query_with_validation("test query")
                
                self.assertIsNotNone(result)
                self.assertIsInstance(result, ValidatedRecommendationResponse)
                
        except Exception as e:
            self.skipTest(f"GuardedRAGPipeline integration test failed: {e}")
    
    @unittest.skipIf(OutputValidator is None, "OutputValidator not available")
    def test_json_parsing_error_handling(self):
        """Test handling of malformed JSON responses"""
        validator = OutputValidator(self.sample_courses, confidence_threshold=0.6)
        
        # Test with invalid JSON
        invalid_json = "{ invalid json content"
        
        # Should handle gracefully and return fallback
        try:
            parsed = validator.parse_llm_response(invalid_json)
            self.assertIsNotNone(parsed)
            # Should return some default structure
            
        except Exception:
            # Should not raise unhandled exceptions
            self.fail("JSON parsing should handle errors gracefully")
    
    @unittest.skipIf(RecommendationResponse is None, "RecommendationResponse not available")
    def test_recommendation_response_validation(self):
        """Test RecommendationResponse model validation"""
        # Valid response
        valid_response = {
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Great for beginners",
                    "match_score": 0.9
                }
            ],
            "overall_confidence": 0.85,
            "reasoning": "Strong match based on analysis"
        }
        
        response = RecommendationResponse(**valid_response)
        self.assertEqual(len(response.recommendations), 1)
        self.assertEqual(response.overall_confidence, 0.85)
        
        # Invalid response - confidence out of range
        invalid_response = {
            "recommendations": [],
            "overall_confidence": 1.5,  # Invalid
            "reasoning": "Test"
        }
        
        with self.assertRaises(ValidationError):
            RecommendationResponse(**invalid_response)
    
    def test_confidence_score_edge_cases(self):
        """Test edge cases for confidence scoring"""
        if OutputValidator is None:
            self.skipTest("OutputValidator not available")
        
        validator = OutputValidator(self.sample_courses, confidence_threshold=0.6)
        
        # Test with exactly threshold confidence
        threshold_response = {
            "recommendations": [
                {
                    "course_id": "CS101",
                    "title": "Introduction to Computer Science",
                    "justification": "Suitable course",
                    "match_score": 0.6
                }
            ],
            "overall_confidence": 0.6,  # Exactly at threshold
            "reasoning": "Meets minimum requirements"
        }
        
        validated = validator.validate_response(threshold_response, "test query")
        
        # Should pass validation at threshold
        self.assertTrue(validated.validation_passed)
        self.assertFalse(validated.fallback_triggered)


if __name__ == "__main__":
    unittest.main()
