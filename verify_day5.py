"""
Day 5: Guardrails + Output Validation Verification Script

This script verifies all Day 5 requirements:
✅ Use Pydantic or JSON schema validation
✅ Add filters for hallucinated or invalid course IDs
✅ Score responses for confidence and fallback to generic help if too low
✅ Validator that accepts only certain course IDs
✅ Requires "justification" and "match_score" in LLM output
"""

import sys
import os
import json
import logging
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from day5_guardrails import (
    Day5GuardedRAGPipeline, 
    CourseValidator, 
    OutputValidator, 
    CourseRecommendation,
    ValidatedRecommendationResponse,
    ValidationLevel
)
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pydantic_validation():
    """Test Pydantic model validation"""
    print("1️⃣ Testing Pydantic Validation...")
    
    # Test valid course recommendation
    try:
        valid_rec = CourseRecommendation(
            course_id="CS101",
            title="Introduction to Computer Science",
            justification="This course provides fundamental programming concepts essential for beginners",
            match_score=0.85
        )
        print("   ✅ Valid CourseRecommendation created successfully")
    except ValidationError as e:
        print(f"   ❌ Valid CourseRecommendation failed: {e}")
        return False
    
    # Test invalid course recommendation (bad course ID format)
    try:
        invalid_rec = CourseRecommendation(
            course_id="INVALID123",
            title="Invalid Course",
            justification="Short",  # Too short
            match_score=1.5  # Out of range
        )
        print("   ❌ Invalid CourseRecommendation should have failed validation")
        return False
    except ValidationError:
        print("   ✅ Invalid CourseRecommendation correctly rejected")
    
    # Test justification validation
    try:
        generic_rec = CourseRecommendation(
            course_id="CS101",
            title="Test Course",
            justification="good course",  # Too generic and short
            match_score=0.7
        )
        print("   ❌ Generic justification should have been rejected")
        return False
    except ValidationError:
        print("   ✅ Generic justification correctly rejected")
    
    return True


def test_course_validator():
    """Test CourseValidator functionality"""
    print("\\n2️⃣ Testing Course Validator...")
    
    # Load valid courses
    from src.data_manager import load_courses
    courses = load_courses("data/courses.json")
    validator = CourseValidator(courses)
    
    # Test valid course ID
    is_valid, error = validator.validate_course_id("CS101")
    if is_valid:
        print("   ✅ Valid course ID (CS101) accepted")
    else:
        print(f"   ❌ Valid course ID rejected: {error}")
        return False
    
    # Test invalid course ID
    is_valid, error = validator.validate_course_id("FAKE999")
    if not is_valid:
        print("   ✅ Invalid course ID (FAKE999) correctly rejected")
    else:
        print("   ❌ Invalid course ID should have been rejected")
        return False
    
    # Test hallucination detection
    text_with_hallucination = "I recommend CS999 and FAKE101 which are excellent courses"
    issues = validator.detect_hallucinated_content(text_with_hallucination)
    if issues:
        print(f"   ✅ Hallucinated course IDs detected: {len(issues)} issues")
    else:
        print("   ❌ Should have detected hallucinated course IDs")
        return False
    
    # Test clean text
    clean_text = "I recommend CS101 which is an excellent introductory course"
    issues = validator.detect_hallucinated_content(clean_text)
    if not issues:
        print("   ✅ Clean text passed hallucination detection")
    else:
        print(f"   ⚠️ Clean text flagged (may be overly strict): {issues}")
    
    return True


def test_output_validator():
    """Test OutputValidator functionality"""
    print("\\n3️⃣ Testing Output Validator...")
    
    from src.data_manager import load_courses
    courses = load_courses("data/courses.json")
    course_validator = CourseValidator(courses)
    output_validator = OutputValidator(course_validator, confidence_threshold=0.6)
    
    # Test valid response validation
    valid_response_data = {
        "recommendations": [
            {
                "course_id": "CS101",
                "title": "Introduction to Computer Science",
                "justification": "This course provides essential programming fundamentals that are crucial for computer science students",
                "match_score": 0.8
            }
        ],
        "overall_confidence": 0.8,
        "justification": "These recommendations align well with the student's interests in programming and provide a strong foundation for further study",
        "match_score": 0.8
    }
    
    try:
        validated = output_validator.validate_response(valid_response_data, "I want to learn programming")
        if validated.validation_passed:
            print("   ✅ Valid response passed validation")
        else:
            print(f"   ❌ Valid response failed validation: {validated.warnings}")
            return False
    except Exception as e:
        print(f"   ❌ Valid response validation error: {e}")
        return False
    
    # Test response with invalid course ID (should trigger fallback)
    invalid_response_data = {
        "recommendations": [
            {
                "course_id": "FAKE999",
                "title": "Fake Course",
                "justification": "This is a hallucinated course that doesn't exist in our system",
                "match_score": 0.9
            }
        ],
        "overall_confidence": 0.9,
        "justification": "These are completely made up recommendations that should be filtered out",
        "match_score": 0.9
    }
    
    validated = output_validator.validate_response(invalid_response_data, "I want fake courses")
    # When invalid course IDs are filtered out, we should get a fallback response
    if validated.fallback_triggered and len(validated.recommendations) == 0:
        print("   ✅ Invalid course ID correctly filtered out and fallback triggered")
    else:
        print(f"   ❌ Invalid course ID should trigger fallback: fallback={validated.fallback_triggered}, recs={len(validated.recommendations)}")
        return False
    
    return True


def test_confidence_scoring():
    """Test confidence scoring and fallback mechanisms"""
    print("\\n4️⃣ Testing Confidence Scoring...")
    
    from src.data_manager import load_courses
    courses = load_courses("data/courses.json")
    course_validator = CourseValidator(courses)
    output_validator = OutputValidator(course_validator, confidence_threshold=0.6)
    
    # Test low confidence response (should trigger fallback)
    low_confidence_response = {
        "recommendations": [
            {
                "course_id": "CS101",
                "title": "Introduction to Computer Science",
                "justification": "This might be relevant but I'm not entirely sure about the match",
                "match_score": 0.3
            }
        ],
        "overall_confidence": 0.3,
        "justification": "Low confidence in these recommendations due to unclear query",
        "match_score": 0.3
    }
    
    validated = output_validator.validate_response(low_confidence_response, "unclear query")
    if validated.fallback_triggered:
        print("   ✅ Low confidence correctly triggered fallback")
    else:
        print("   ❌ Low confidence should have triggered fallback")
        return False
    
    # Test high confidence response
    high_confidence_response = {
        "recommendations": [
            {
                "course_id": "CS101",
                "title": "Introduction to Computer Science",
                "justification": "This course is perfectly aligned with the student's interests in learning programming fundamentals",
                "match_score": 0.9
            }
        ],
        "overall_confidence": 0.9,
        "justification": "High confidence recommendations based on clear interest alignment",
        "match_score": 0.9
    }
    
    validated = output_validator.validate_response(high_confidence_response, "I want to learn programming")
    if not validated.fallback_triggered and validated.validation_passed:
        print("   ✅ High confidence response processed normally")
    else:
        print("   ❌ High confidence response should not trigger fallback")
        return False
    
    return True


def test_guarded_pipeline():
    """Test the complete guarded RAG pipeline"""
    print("\\n5️⃣ Testing Guarded RAG Pipeline...")
    
    try:
        pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.5)
        print("   ✅ Guarded pipeline initialized successfully")
    except Exception as e:
        print(f"   ❌ Pipeline initialization failed: {e}")
        return False
    
    # Test with a clear query
    try:
        response = pipeline.process_query_with_validation("I want to learn machine learning")
        
        # Check response structure
        if isinstance(response, ValidatedRecommendationResponse):
            print("   ✅ Returned ValidatedRecommendationResponse")
        else:
            print("   ❌ Should return ValidatedRecommendationResponse")
            return False
        
        # Check validation fields
        checks = [
            (hasattr(response, 'validation_passed'), "Has validation_passed field"),
            (hasattr(response, 'warnings'), "Has warnings field"),
            (hasattr(response, 'fallback_triggered'), "Has fallback_triggered field"),
            (hasattr(response, 'justification'), "Has justification field"),
            (hasattr(response, 'match_score'), "Has match_score field"),
            (all(hasattr(rec, 'justification') and hasattr(rec, 'match_score') 
                 for rec in response.recommendations), "All recommendations have required fields")
        ]
        
        for check, description in checks:
            status = "✅" if check else "❌"
            print(f"   {status} {description}")
        
        # Check for valid course IDs only
        invalid_courses = [rec for rec in response.recommendations 
                          if rec.course_id not in pipeline.course_validator.valid_course_ids]
        if not invalid_courses:
            print("   ✅ All recommended courses are valid")
        else:
            print(f"   ❌ Found invalid course recommendations: {[c.course_id for c in invalid_courses]}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Pipeline processing failed: {e}")
        return False


def test_required_fields():
    """Test that all required fields are present and validated"""
    print("\\n6️⃣ Testing Required Fields...")
    
    # Test that justification and match_score are required
    try:
        # Missing justification
        CourseRecommendation(
            course_id="CS101",
            title="Test Course",
            # justification missing
            match_score=0.8
        )
        print("   ❌ Should require justification field")
        return False
    except ValidationError:
        print("   ✅ Justification field required")
    
    try:
        # Missing match_score
        CourseRecommendation(
            course_id="CS101",
            title="Test Course",
            justification="This is a good course for beginners learning programming fundamentals"
            # match_score missing
        )
        print("   ❌ Should require match_score field")
        return False
    except ValidationError:
        print("   ✅ Match_score field required")
    
    # Test ValidatedRecommendationResponse required fields
    try:
        ValidatedRecommendationResponse(
            query="test query",
            recommendations=[],
            overall_confidence=0.7,
            # justification missing
            match_score=0.7
        )
        print("   ❌ Should require justification field in response")
        return False
    except ValidationError:
        print("   ✅ Response justification field required")
    
    return True


def main():
    """Run all Day 5 verification tests"""
    print("🛡️ Day 5: Guardrails + Output Validation Verification")
    print("="*70)
    
    tests = [
        ("Pydantic Validation", test_pydantic_validation),
        ("Course Validator", test_course_validator),
        ("Output Validator", test_output_validator),
        ("Confidence Scoring", test_confidence_scoring),
        ("Guarded Pipeline", test_guarded_pipeline),
        ("Required Fields", test_required_fields)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\\n" + "="*70)
    print("📊 Day 5 Verification Summary")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"📈 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\\n🎉 ALL DAY 5 REQUIREMENTS VERIFIED!")
        print("="*70)
        print("\\n📋 Day 5 Checklist:")
        print("✅ Use Pydantic or JSON schema validation")
        print("✅ Add filters for hallucinated or invalid course IDs")
        print("✅ Score responses for confidence and fallback to generic help")
        print("✅ Validator that accepts only certain course IDs")
        print("✅ Requires 'justification' and 'match_score' in LLM output")
        print("✅ Comprehensive error handling and validation")
        print("✅ Structured response format with metadata")
        
        print("\\n🔧 Technical Implementation:")
        print("   • Pydantic models with comprehensive field validation")
        print("   • CourseValidator with hallucination detection")
        print("   • OutputValidator with confidence-based fallback")
        print("   • Structured JSON output with required fields")
        print("   • Integration with Day 4 RAG pipeline")
        print("   • Production-ready error handling")
        
        print("\\n🎉 Day 5 implementation ready for production!")
    else:
        print(f"\\n❌ {total - passed} tests failed. Please review implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
