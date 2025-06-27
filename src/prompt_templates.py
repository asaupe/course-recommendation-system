"""
Prompt Templates Module

Contains all the prompt templates used for AI interactions in the course recommendation system.
"""

from typing import Dict, Any, List


class PromptTemplates:
    """
    Class containing all prompt templates for the course recommendation system.
    """
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Get the system prompt for the AI assistant.
        
        Returns:
            System prompt string
        """
        return """You are an expert academic advisor AI that helps students choose the best courses for their degree program. Your recommendations should be:

1. **Personalized**: Consider the student's major, year, interests, and learning preferences
2. **Strategic**: Align with graduation requirements and academic goals
3. **Practical**: Consider prerequisites, course difficulty, and workload balance
4. **Explanatory**: Provide clear reasons for each recommendation

When making recommendations:
- Prioritize courses that fulfill graduation requirements
- Match course difficulty to student preferences
- Consider the student's expressed interests and career goals
- Suggest a balanced mix of required and elective courses
- Explain why each course is beneficial for the student

Response format: Provide a JSON array of course recommendations with detailed explanations."""
    
    @staticmethod
    def get_recommendation_prompt(
        user_profile: Dict[str, Any], 
        candidate_courses: List[Dict[str, Any]], 
        num_recommendations: int = 5
    ) -> str:
        """
        Generate a recommendation prompt based on user profile and candidate courses.
        
        Args:
            user_profile: User profile information
            candidate_courses: List of candidate courses from RAG search
            num_recommendations: Number of recommendations to generate
            
        Returns:
            Formatted prompt string
        """
        # Extract user information
        name = user_profile.get('name', 'Student')
        major = user_profile.get('major', 'Undeclared')
        year = user_profile.get('year', 'Freshman')
        remaining_credits = user_profile.get('remaining_credits', 0)
        required_categories = user_profile.get('required_categories', [])
        interests = user_profile.get('interests', '')
        learning_style = user_profile.get('learning_style', 'Mixed')
        difficulty_preference = user_profile.get('difficulty_preference', 3)
        
        # Format candidate courses
        courses_text = ""
        for course in candidate_courses[:15]:  # Limit to avoid token limits
            courses_text += f"""
Course: {course.get('code', 'N/A')} - {course.get('title', 'N/A')}
Credits: {course.get('credits', 0)}
Difficulty: {course.get('difficulty', 0)}/5
Category: {course.get('category', 'N/A')}
Description: {course.get('description', 'No description available')}
Prerequisites: {course.get('prerequisites', 'None')}
---"""
        
        prompt = f"""
Please recommend {num_recommendations} courses for this student profile:

**Student Information:**
- Name: {name}
- Major: {major}
- Academic Year: {year}
- Remaining Credits: {remaining_credits}
- Required Categories: {', '.join(required_categories)}
- Interests: {interests}
- Learning Style: {learning_style}
- Preferred Difficulty: {difficulty_preference}/5

**Available Courses:**
{courses_text}

**Instructions:**
1. Select {num_recommendations} courses that best match the student's profile
2. Prioritize courses from required categories: {', '.join(required_categories)}
3. Consider the student's interests: {interests}
4. Match difficulty preference: {difficulty_preference}/5
5. Ensure a good balance of required and interesting courses

**Required Response Format:**
Return a JSON array with exactly {num_recommendations} course recommendations. Each recommendation should have this structure:
```json
[
  {{
    "code": "course_code",
    "title": "Course Title",
    "description": "Course description",
    "credits": credits_number,
    "difficulty": difficulty_rating,
    "category": "course_category",
    "semester": "availability",
    "prerequisites": "prerequisite_info",
    "reason": "Detailed explanation of why this course is recommended for this specific student, considering their major, interests, and requirements"
  }}
]
```

Make sure each recommendation includes a personalized explanation that connects to the student's specific profile, interests, and graduation requirements.
"""
        
        return prompt
    
    @staticmethod
    def get_course_analysis_prompt(course_data: Dict[str, Any]) -> str:
        """
        Generate a prompt for analyzing a specific course.
        
        Args:
            course_data: Course information dictionary
            
        Returns:
            Formatted prompt string
        """
        return f"""
Analyze this course and provide insights:

Course: {course_data.get('code', 'N/A')} - {course_data.get('title', 'N/A')}
Description: {course_data.get('description', 'No description')}
Credits: {course_data.get('credits', 0)}
Category: {course_data.get('category', 'N/A')}

Provide analysis on:
1. Key learning outcomes
2. Skills developed
3. Career relevance
4. Prerequisites knowledge needed
5. Recommended for students interested in what areas
"""
    
    @staticmethod
    def get_graduation_planning_prompt(
        user_profile: Dict[str, Any], 
        completed_courses: List[str],
        remaining_requirements: Dict[str, Any]
    ) -> str:
        """
        Generate a prompt for graduation planning assistance.
        
        Args:
            user_profile: User profile information
            completed_courses: List of completed course codes
            remaining_requirements: Dictionary of remaining requirements
            
        Returns:
            Formatted prompt string
        """
        major = user_profile.get('major', 'Undeclared')
        year = user_profile.get('year', 'Freshman')
        remaining_credits = user_profile.get('remaining_credits', 0)
        
        completed_text = ', '.join(completed_courses) if completed_courses else 'None listed'
        
        requirements_text = ""
        for category, count in remaining_requirements.items():
            requirements_text += f"- {category}: {count} courses needed\n"
        
        return f"""
Create a graduation plan for this student:

**Student Profile:**
- Major: {major}
- Current Year: {year}
- Remaining Credits: {remaining_credits}

**Completed Courses:** {completed_text}

**Remaining Requirements:**
{requirements_text}

Please provide:
1. Recommended course sequence by semester
2. Priority courses to take next
3. Potential scheduling conflicts to avoid
4. Tips for balancing workload
5. Timeline to graduation
"""
    
    @staticmethod
    def get_interest_matching_prompt(interests: str, available_courses: List[Dict[str, Any]]) -> str:
        """
        Generate a prompt for matching student interests with courses.
        
        Args:
            interests: Student's interest description
            available_courses: List of available courses
            
        Returns:
            Formatted prompt string
        """
        courses_text = ""
        for course in available_courses[:10]:  # Limit courses
            courses_text += f"- {course.get('code', 'N/A')}: {course.get('title', 'N/A')} - {course.get('description', 'No description')[:100]}...\n"
        
        return f"""
Student Interests: {interests}

Available Courses:
{courses_text}

Based on the student's interests, rank these courses from most to least relevant. For each course, explain how it connects to their interests and what specific aspects would appeal to them.

Provide detailed reasoning for the top 5 matches.
"""
