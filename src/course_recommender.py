"""
Course Recommender Module

This module implements the core course recommendation logic using
OpenAI's GPT API and RAG (Retrieval-Augmented Generation) techniques.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .rag_system import RAGSystem
from .prompt_templates import PromptTemplates
from .data_manager import DataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourseRecommender:
    """
    Main class for generating course recommendations using AI and RAG.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Course Recommender.
        
        Args:
            api_key: OpenAI API key. If None, will use environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.rag_system = RAGSystem()
        self.prompt_templates = PromptTemplates()
        self.data_manager = DataManager()
        
        # Initialize RAG system with course data
        self._initialize_rag_system()
    
    def _initialize_rag_system(self) -> None:
        """Initialize the RAG system with course data."""
        try:
            courses = self.data_manager.load_courses()
            if courses:
                self.rag_system.add_courses(courses)
                logger.info(f"Initialized RAG system with {len(courses)} courses")
            else:
                logger.warning("No courses found to initialize RAG system")
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
    
    def get_recommendations(self, user_profile: Dict[str, Any], num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get course recommendations for a user based on their profile.
        
        Args:
            user_profile: Dictionary containing user information
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended courses with explanations
        """
        try:
            # Extract interests and requirements from user profile
            interests = user_profile.get("interests", "")
            required_categories = user_profile.get("required_categories", [])
            remaining_credits = user_profile.get("remaining_credits", 0)
            difficulty_preference = user_profile.get("difficulty_preference", 3)
            
            # Use RAG to find relevant courses
            relevant_courses = self.rag_system.search_courses(
                query=interests,
                categories=required_categories,
                max_results=num_recommendations * 2  # Get more to filter from
            )
            
            if not relevant_courses:
                # Fallback to sample courses if no search results
                relevant_courses = self._get_sample_courses()
            
            # Generate AI-powered recommendations
            recommendations = self._generate_ai_recommendations(
                user_profile=user_profile,
                candidate_courses=relevant_courses,
                num_recommendations=num_recommendations
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Return sample recommendations as fallback
            return self._get_sample_recommendations(user_profile)
    
    def _generate_ai_recommendations(
        self, 
        user_profile: Dict[str, Any], 
        candidate_courses: List[Dict[str, Any]], 
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered course recommendations.
        
        Args:
            user_profile: User profile information
            candidate_courses: List of candidate courses from RAG search
            num_recommendations: Number of recommendations to generate
            
        Returns:
            List of recommended courses with AI-generated explanations
        """
        try:
            # Prepare the prompt
            prompt = self.prompt_templates.get_recommendation_prompt(
                user_profile=user_profile,
                candidate_courses=candidate_courses,
                num_recommendations=num_recommendations
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompt_templates.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            recommendations_text = response.choices[0].message.content
            recommendations = self._parse_ai_response(recommendations_text, candidate_courses)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in AI recommendation generation: {e}")
            # Fallback to rule-based recommendations
            return self._get_rule_based_recommendations(user_profile, candidate_courses, num_recommendations)
    
    def _parse_ai_response(self, response_text: str, candidate_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse the AI response and match with candidate courses.
        
        Args:
            response_text: Raw response from AI
            candidate_courses: List of candidate courses
            
        Returns:
            List of structured course recommendations
        """
        recommendations = []
        
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('['):
                parsed = json.loads(response_text)
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse text response and match with courses
        lines = response_text.split('\n')
        course_map = {course['code']: course for course in candidate_courses}
        
        for line in lines:
            if any(code in line for code in course_map.keys()):
                for code, course in course_map.items():
                    if code in line:
                        recommendation = course.copy()
                        recommendation['reason'] = line.split(':')[-1].strip() if ':' in line else "AI recommended based on your profile"
                        recommendations.append(recommendation)
                        break
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_rule_based_recommendations(
        self, 
        user_profile: Dict[str, Any], 
        candidate_courses: List[Dict[str, Any]], 
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """
        Generate rule-based recommendations as fallback.
        
        Args:
            user_profile: User profile information
            candidate_courses: List of candidate courses
            num_recommendations: Number of recommendations to generate
            
        Returns:
            List of rule-based course recommendations
        """
        recommendations = []
        difficulty_pref = user_profile.get("difficulty_preference", 3)
        required_categories = user_profile.get("required_categories", [])
        
        # Score courses based on simple rules
        scored_courses = []
        for course in candidate_courses:
            score = 0
            
            # Category match
            if course.get('category') in required_categories:
                score += 3
            
            # Difficulty match
            course_difficulty = course.get('difficulty', 3)
            difficulty_diff = abs(course_difficulty - difficulty_pref)
            score += max(0, 3 - difficulty_diff)
            
            # Interest match (simple keyword matching)
            interests = user_profile.get("interests", "").lower()
            course_desc = course.get('description', '').lower()
            if any(word in course_desc for word in interests.split()):
                score += 2
            
            scored_courses.append((score, course))
        
        # Sort by score and take top recommendations
        scored_courses.sort(key=lambda x: x[0], reverse=True)
        
        for score, course in scored_courses[:num_recommendations]:
            recommendation = course.copy()
            recommendation['reason'] = f"Matches your requirements and preferences (score: {score})"
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_sample_courses(self) -> List[Dict[str, Any]]:
        """Get sample courses for demonstration purposes."""
        return [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming and computer science",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "MATH201",
                "title": "Calculus I",
                "description": "Differential calculus and applications",
                "credits": 4,
                "difficulty": 3,
                "category": "Math/Science",
                "semester": "Fall/Spring",
                "prerequisites": "Pre-calculus"
            },
            {
                "code": "ENG102",
                "title": "English Composition",
                "description": "Academic writing and critical thinking",
                "credits": 3,
                "difficulty": 2,
                "category": "General Education",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            }
        ]
    
    def _get_sample_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get sample recommendations for demonstration purposes."""
        sample_courses = self._get_sample_courses()
        
        for course in sample_courses:
            course['reason'] = f"Recommended based on your {user_profile.get('major', 'program')} requirements"
        
        return sample_courses
