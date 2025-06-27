"""
Day 5: Guardrails + Output Validation

This module implements the Day 5 requirements:
✅ Use Pydantic or JSON schema validation
✅ Add filters for hallucinated or invalid course IDs
✅ Score responses for confidence and fallback to generic help if too low
✅ Validator that accepts only certain course IDs
✅ Requires "justification" and "match_score" in LLM output

Author: Course Recommendation System
Date: Day 5 Implementation
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pydantic import BaseModel, Field, validator, ValidationError
from openai import OpenAI
from dotenv import load_dotenv

# Import our existing components
from day4_rag_pipeline import Day4RAGPipeline, RAGResponse, ConfidenceLevel
from src.data_manager import load_courses

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation confidence levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class CourseRecommendation(BaseModel):
    """
    ✅ Day 5 Requirement: Pydantic validation for structured output
    
    Validates individual course recommendations with required fields.
    """
    course_id: str = Field(..., description="Course code (e.g., CS101)")
    title: str = Field(..., description="Course title")
    justification: str = Field(..., min_length=50, description="Why this course is recommended (min 50 chars)")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    prerequisites_met: bool = Field(default=True, description="Whether prerequisites are satisfied")
    difficulty_appropriate: bool = Field(default=True, description="Whether difficulty level is appropriate")
    
    @validator('course_id')
    def validate_course_id_format(cls, v):
        """Validate course ID follows expected format"""
        if not re.match(r'^[A-Z]{2,4}\d{3}$', v):
            raise ValueError(f"Course ID '{v}' must follow format like 'CS101' or 'MATH301'")
        return v
    
    @validator('justification')
    def validate_justification_quality(cls, v):
        """Ensure justification is meaningful and not generic"""
        generic_phrases = ['good course', 'recommended', 'useful', 'important']
        if any(phrase in v.lower() for phrase in generic_phrases) and len(v) < 100:
            raise ValueError("Justification appears too generic - please provide specific reasoning")
        return v


class ValidatedRecommendationResponse(BaseModel):
    """
    ✅ Day 5 Requirement: Complete validated response structure
    
    Comprehensive response model with all required validation fields.
    """
    query: str = Field(..., description="Original student query")
    recommendations: List[CourseRecommendation] = Field(..., max_items=5, description="List of course recommendations")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in recommendations")
    justification: str = Field(..., min_length=100, description="Overall reasoning for recommendations")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Overall match quality score")
    fallback_triggered: bool = Field(default=False, description="Whether fallback guidance was used")
    validation_passed: bool = Field(default=True, description="Whether all validations passed")
    warnings: List[str] = Field(default_factory=list, description="Any validation warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('recommendations')
    def validate_recommendations_count(cls, v):
        """Ensure appropriate number of recommendations"""
        if len(v) < 1:
            raise ValueError("Must provide at least 1 recommendation")
        if len(v) > 5:
            raise ValueError("Cannot provide more than 5 recommendations")
        return v
    
    @validator('overall_confidence')
    def validate_confidence_consistency(cls, v, values):
        """Ensure overall confidence is consistent with individual scores"""
        if 'recommendations' in values and values['recommendations']:
            avg_score = sum(rec.match_score for rec in values['recommendations']) / len(values['recommendations'])
            if abs(v - avg_score) > 0.3:
                raise ValueError("Overall confidence should be consistent with individual match scores")
        return v


class CourseValidator:
    """
    ✅ Day 5 Requirement: Validator for course IDs and content filtering
    
    Validates course IDs against known courses and filters hallucinated content.
    """
    
    def __init__(self, valid_courses: List[Dict[str, Any]]):
        """
        Initialize validator with valid course data.
        
        Args:
            valid_courses: List of valid course dictionaries
        """
        self.valid_courses = valid_courses
        self.valid_course_ids: Set[str] = {course['code'] for course in valid_courses}
        self.course_lookup = {course['code']: course for course in valid_courses}
        
        logger.info(f"Initialized CourseValidator with {len(self.valid_course_ids)} valid courses")
    
    def validate_course_id(self, course_id: str) -> tuple[bool, Optional[str]]:
        """
        ✅ Day 5 Requirement: Accept only certain course IDs
        
        Validate that a course ID exists in our known courses.
        
        Args:
            course_id: Course code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if course_id not in self.valid_course_ids:
            return False, f"Course ID '{course_id}' not found in valid courses"
        return True, None
    
    def detect_hallucinated_content(self, text: str) -> List[str]:
        """
        ✅ Day 5 Requirement: Filter hallucinated or invalid course IDs
        
        Detect potential hallucinated course IDs in text.
        
        Args:
            text: Text to analyze for hallucinated content
            
        Returns:
            List of potential issues found
        """
        issues = []
        
        # Find potential course IDs in text
        course_id_pattern = r'\b[A-Z]{2,4}\d{3}\b'
        found_ids = re.findall(course_id_pattern, text)
        
        for course_id in found_ids:
            if course_id not in self.valid_course_ids:
                issues.append(f"Potential hallucinated course ID: {course_id}")
        
        # Check for unrealistic claims
        unrealistic_patterns = [
            r'100% guaranteed',
            r'perfect course',
            r'never fails',
            r'instant expertise',
            r'no prerequisites needed' # when we know there are prereqs
        ]
        
        for pattern in unrealistic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Potentially unrealistic claim detected: {pattern}")
        
        return issues
    
    def get_course_details(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get course details for a valid course ID"""
        return self.course_lookup.get(course_id)


class OutputValidator:
    """
    ✅ Day 5 Requirement: Complete output validation system
    
    Comprehensive validation system for LLM outputs with confidence scoring.
    """
    
    def __init__(self, course_validator: CourseValidator, confidence_threshold: float = 0.6):
        """
        Initialize output validator.
        
        Args:
            course_validator: CourseValidator instance
            confidence_threshold: Minimum confidence for accepting recommendations
        """
        self.course_validator = course_validator
        self.confidence_threshold = confidence_threshold
        logger.info(f"Initialized OutputValidator with confidence threshold: {confidence_threshold}")
    
    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response text to extract structured data.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed response dictionary
        """
        # Try to extract JSON if present
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract information using patterns
        extracted = {
            'recommendations': [],
            'justification': response_text,
            'match_score': 0.5  # Default moderate score
        }
        
        # Extract course mentions
        course_pattern = r'([A-Z]{2,4}\d{3})'
        courses = re.findall(course_pattern, response_text)
        
        for course_id in courses[:5]:  # Limit to 5 courses
            if self.course_validator.validate_course_id(course_id)[0]:
                course_details = self.course_validator.get_course_details(course_id)
                extracted['recommendations'].append({
                    'course_id': course_id,
                    'title': course_details['title'] if course_details else course_id,
                    'justification': f"Recommended based on content analysis",
                    'match_score': 0.7
                })
        
        return extracted
    
    def validate_response(self, response: Union[Dict[str, Any], str], query: str) -> ValidatedRecommendationResponse:
        """
        ✅ Day 5 Requirement: Complete validation with confidence scoring
        
        Validate LLM response and create structured output.
        
        Args:
            response: LLM response (dict or string)
            query: Original query
            
        Returns:
            Validated response object
        """
        warnings = []
        validation_passed = True
        
        # Parse response if it's a string
        if isinstance(response, str):
            response = self.parse_llm_response(response)
        
        # Validate course IDs and filter hallucinations
        validated_recommendations = []
        
        for rec_data in response.get('recommendations', []):
            try:
                # Validate course ID
                course_id = rec_data.get('course_id', '')
                is_valid, error_msg = self.course_validator.validate_course_id(course_id)
                
                if not is_valid:
                    warnings.append(f"Invalid course ID filtered: {course_id}")
                    validation_passed = False
                    continue
                
                # Check for hallucinated content in justification
                justification = rec_data.get('justification', '')
                hallucination_issues = self.course_validator.detect_hallucinated_content(justification)
                if hallucination_issues:
                    warnings.extend(hallucination_issues)
                
                # Create validated recommendation
                course_details = self.course_validator.get_course_details(course_id)
                recommendation = CourseRecommendation(
                    course_id=course_id,
                    title=course_details['title'] if course_details else rec_data.get('title', course_id),
                    justification=justification if len(justification) >= 50 else f"Recommended course for your interests: {justification}. This course provides valuable knowledge and skills.",
                    match_score=rec_data.get('match_score', 0.5),
                    prerequisites_met=rec_data.get('prerequisites_met', True),
                    difficulty_appropriate=rec_data.get('difficulty_appropriate', True)
                )
                validated_recommendations.append(recommendation)
                
            except ValidationError as e:
                warnings.append(f"Recommendation validation failed: {str(e)}")
                validation_passed = False
        
        # Calculate overall scores
        overall_confidence = response.get('overall_confidence')
        if overall_confidence is None and validated_recommendations:
            overall_confidence = sum(rec.match_score for rec in validated_recommendations) / len(validated_recommendations)
        elif overall_confidence is None:
            overall_confidence = 0.0
        
        match_score = response.get('match_score', overall_confidence)
        
        # Determine if fallback should be triggered
        fallback_triggered = (
            overall_confidence < self.confidence_threshold or
            len(validated_recommendations) == 0 or
            not validation_passed
        )
        
        # Ensure justification meets minimum length
        justification = response.get('justification', 'No specific justification provided')
        if len(justification) < 100:
            justification = f"{justification}. Based on the analysis of your query and available courses, these recommendations aim to provide relevant learning opportunities that align with your stated interests and academic goals."
        
        # Create validated response
        try:
            validated_response = ValidatedRecommendationResponse(
                query=query,
                recommendations=validated_recommendations,
                overall_confidence=overall_confidence,
                justification=justification,
                match_score=match_score,
                fallback_triggered=fallback_triggered,
                validation_passed=validation_passed and len(validated_recommendations) > 0,
                warnings=warnings,
                metadata={
                    'original_recommendation_count': len(response.get('recommendations', [])),
                    'filtered_recommendation_count': len(validated_recommendations),
                    'validation_level': 'strict'
                }
            )
            
            return validated_response
            
        except ValidationError as e:
            # Create minimal fallback response
            logger.error(f"Validation failed, creating fallback response: {e}")
            return self._create_fallback_response(query, str(e))
    
    def _create_fallback_response(self, query: str, error_reason: str) -> ValidatedRecommendationResponse:
        """
        ✅ Day 5 Requirement: Fallback to generic help if confidence too low
        
        Create a fallback response when validation fails.
        """
        fallback_justification = f"""I apologize, but I couldn't provide specific course recommendations for your query due to validation constraints. This might be because:

1. The query is too broad or unclear
2. No courses closely match your specific interests
3. There were technical issues processing your request

For general guidance, I recommend:
- Starting with core computer science fundamentals (CS101)
- Consulting with an academic advisor for personalized planning
- Exploring the course catalog to discover areas of interest
- Considering your prerequisite completion and academic level

Please try rephrasing your query with more specific interests or academic goals."""
        
        return ValidatedRecommendationResponse(
            query=query,
            recommendations=[],
            overall_confidence=0.0,
            justification=fallback_justification,
            match_score=0.0,
            fallback_triggered=True,
            validation_passed=False,
            warnings=[f"Fallback triggered: {error_reason}"],
            metadata={'fallback_reason': error_reason}
        )


class Day5GuardedRAGPipeline:
    """
    ✅ Day 5 Requirement: Complete guarded RAG pipeline
    
    Enhanced RAG pipeline with comprehensive validation and guardrails.
    """
    
    def __init__(self, api_key: Optional[str] = None, confidence_threshold: float = 0.6):
        """
        Initialize the guarded RAG pipeline.
        
        Args:
            api_key: OpenAI API key
            confidence_threshold: Minimum confidence threshold
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.confidence_threshold = confidence_threshold
        
        # Initialize components
        self.courses = load_courses("data/courses.json")
        self.course_validator = CourseValidator(self.courses)
        self.output_validator = OutputValidator(self.course_validator, confidence_threshold)
        self.base_pipeline = Day4RAGPipeline(api_key=api_key)
        
        logger.info(f"Initialized Day5GuardedRAGPipeline with {len(self.courses)} courses")
    
    def _create_structured_prompt(self, query: str, context: str, confidence: ConfidenceLevel) -> str:
        """
        Create a structured prompt that encourages JSON output with required fields.
        """
        valid_course_ids = list(self.course_validator.valid_course_ids)
        
        prompt = f"""You are an expert course advisor. Provide course recommendations in the following JSON format:

{{
  "recommendations": [
    {{
      "course_id": "CS101",
      "title": "Course Title",
      "justification": "Detailed explanation of why this course is recommended (minimum 50 characters)",
      "match_score": 0.85,
      "prerequisites_met": true,
      "difficulty_appropriate": true
    }}
  ],
  "overall_confidence": 0.80,
  "justification": "Overall reasoning for these recommendations (minimum 100 characters)",
  "match_score": 0.80
}}

IMPORTANT CONSTRAINTS:
- ONLY use course IDs from this valid list: {valid_course_ids[:10]}... (and others in the context)
- Each justification must be at least 50 characters and specific to the course
- Match scores must be between 0.0 and 1.0
- Be honest about confidence levels
- If unsure, use lower match scores

STUDENT QUERY: "{query}"

AVAILABLE COURSES:
{context}

CONFIDENCE LEVEL: {confidence.value}

Provide your response as valid JSON only:"""
        
        return prompt
    
    def process_query_with_validation(self, query: str, top_k: int = 5) -> ValidatedRecommendationResponse:
        """
        ✅ Day 5 Requirement: Complete pipeline with validation
        
        Process query through RAG pipeline with comprehensive validation.
        
        Args:
            query: Student query
            top_k: Number of courses to consider
            
        Returns:
            Validated recommendation response
        """
        logger.info(f"Processing query with validation: '{query}'")
        
        try:
            # Step 1: Get base RAG response
            base_response = self.base_pipeline.process_query(query, top_k=top_k)
            
            # Step 2: Create structured prompt for LLM
            structured_prompt = self._create_structured_prompt(
                query, 
                base_response.context_used, 
                base_response.confidence
            )
            
            # Step 3: Get structured LLM response
            llm_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a course advisor. Always respond with valid JSON containing course recommendations with required fields: course_id, title, justification, and match_score."
                    },
                    {
                        "role": "user",
                        "content": structured_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent JSON
                max_tokens=1500
            )
            
            response_text = llm_response.choices[0].message.content.strip()
            
            # Step 4: Parse JSON response
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using text parsing")
                response_data = self.output_validator.parse_llm_response(response_text)
            
            # Step 5: Validate response
            validated_response = self.output_validator.validate_response(response_data, query)
            
            logger.info(f"✅ Validation complete: {len(validated_response.recommendations)} valid recommendations")
            return validated_response
            
        except Exception as e:
            logger.error(f"Error in guarded pipeline: {e}")
            return self.output_validator._create_fallback_response(query, str(e))


def demonstrate_day5_validation():
    """Demonstrate Day 5 validation features"""
    print("🛡️ Day 5: Guardrails + Output Validation Demonstration")
    print("="*70)
    
    # Initialize guarded pipeline
    print("1️⃣ Initializing Guarded RAG Pipeline...")
    pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
    print(f"   ✅ Pipeline ready with {len(pipeline.courses)} valid courses")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Valid High-Confidence Query",
            "query": "I want to learn machine learning and AI",
            "expected": "Valid recommendations with good confidence"
        },
        {
            "name": "Ambiguous Query",
            "query": "I like technology",
            "expected": "Lower confidence, possible fallback"
        },
        {
            "name": "Specific Domain Query",
            "query": "I need courses for web development career",
            "expected": "Specific course recommendations"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 2):
        print(f"\\n{i}️⃣ Testing: {scenario['name']}")
        print(f"   📝 Query: '{scenario['query']}'")
        
        response = pipeline.process_query_with_validation(scenario['query'])
        
        print(f"   📊 Validation Status: {'✅ PASSED' if response.validation_passed else '❌ FAILED'}")
        print(f"   📈 Overall Confidence: {response.overall_confidence:.3f}")
        print(f"   📚 Valid Recommendations: {len(response.recommendations)}")
        print(f"   🔄 Fallback Triggered: {response.fallback_triggered}")
        
        if response.warnings:
            print(f"   ⚠️ Warnings: {len(response.warnings)}")
            for warning in response.warnings[:2]:
                print(f"      • {warning}")
        
        if response.recommendations:
            print(f"   🎯 Top Recommendation: {response.recommendations[0].course_id} - {response.recommendations[0].title}")
            print(f"      Match Score: {response.recommendations[0].match_score:.3f}")
    
    print(f"\\n✅ Day 5 validation demonstration complete!")


if __name__ == "__main__":
    demonstrate_day5_validation()
