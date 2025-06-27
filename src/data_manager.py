"""
Data Manager Module

Handles loading, saving, and managing course and graduation requirement data.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages course data and graduation requirements.
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the Data Manager.
        
        Args:
            data_directory: Directory containing data files
        """
        self.data_directory = data_directory
        self.courses_file = os.path.join(data_directory, "courses.json")
        self.requirements_file = os.path.join(data_directory, "requirements.json")
        
        # Ensure data directory exists
        os.makedirs(data_directory, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self) -> None:
        """Initialize data files with sample data if they don't exist."""
        if not os.path.exists(self.courses_file):
            sample_courses = self._get_sample_courses()
            self.save_courses(sample_courses)
            logger.info(f"Initialized {self.courses_file} with sample data")
        
        if not os.path.exists(self.requirements_file):
            sample_requirements = self._get_sample_requirements()
            self.save_requirements(sample_requirements)
            logger.info(f"Initialized {self.requirements_file} with sample data")
    
    def load_courses(self) -> List[Dict[str, Any]]:
        """
        Load courses from the data file.
        
        Returns:
            List of course dictionaries
        """
        try:
            with open(self.courses_file, 'r', encoding='utf-8') as f:
                courses = json.load(f)
            logger.info(f"Loaded {len(courses)} courses from {self.courses_file}")
            return courses
        except Exception as e:
            logger.error(f"Error loading courses: {e}")
            return self._get_sample_courses()
    
    def save_courses(self, courses: List[Dict[str, Any]]) -> bool:
        """
        Save courses to the data file.
        
        Args:
            courses: List of course dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.courses_file, 'w', encoding='utf-8') as f:
                json.dump(courses, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(courses)} courses to {self.courses_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving courses: {e}")
            return False
    
    def load_requirements(self) -> Dict[str, Any]:
        """
        Load graduation requirements from the data file.
        
        Returns:
            Dictionary of graduation requirements
        """
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                requirements = json.load(f)
            logger.info(f"Loaded requirements from {self.requirements_file}")
            return requirements
        except Exception as e:
            logger.error(f"Error loading requirements: {e}")
            return self._get_sample_requirements()
    
    def save_requirements(self, requirements: Dict[str, Any]) -> bool:
        """
        Save graduation requirements to the data file.
        
        Args:
            requirements: Dictionary of graduation requirements
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                json.dump(requirements, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved requirements to {self.requirements_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving requirements: {e}")
            return False
    
    def get_courses_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get courses filtered by category.
        
        Args:
            category: Course category to filter by
            
        Returns:
            List of courses in the specified category
        """
        courses = self.load_courses()
        return [course for course in courses if course.get('category') == category]
    
    def get_courses_by_difficulty(self, min_difficulty: int = 1, max_difficulty: int = 5) -> List[Dict[str, Any]]:
        """
        Get courses filtered by difficulty range.
        
        Args:
            min_difficulty: Minimum difficulty level
            max_difficulty: Maximum difficulty level
            
        Returns:
            List of courses within the difficulty range
        """
        courses = self.load_courses()
        return [
            course for course in courses 
            if min_difficulty <= course.get('difficulty', 3) <= max_difficulty
        ]
    
    def search_courses(self, query: str) -> List[Dict[str, Any]]:
        """
        Search courses by title, code, or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching courses
        """
        courses = self.load_courses()
        query_lower = query.lower()
        
        matching_courses = []
        for course in courses:
            searchable_text = f"{course.get('code', '')} {course.get('title', '')} {course.get('description', '')}".lower()
            if query_lower in searchable_text:
                matching_courses.append(course)
        
        return matching_courses
    
    def get_course_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific course by its code.
        
        Args:
            course_code: Course code to search for
            
        Returns:
            Course dictionary if found, None otherwise
        """
        courses = self.load_courses()
        for course in courses:
            if course.get('code', '').upper() == course_code.upper():
                return course
        return None
    
    def add_course(self, course: Dict[str, Any]) -> bool:
        """
        Add a new course to the database.
        
        Args:
            course: Course dictionary to add
            
        Returns:
            True if successful, False otherwise
        """
        courses = self.load_courses()
        
        # Check if course already exists
        if any(c.get('code') == course.get('code') for c in courses):
            logger.warning(f"Course {course.get('code')} already exists")
            return False
        
        courses.append(course)
        return self.save_courses(courses)
    
    def update_course(self, course_code: str, updated_course: Dict[str, Any]) -> bool:
        """
        Update an existing course.
        
        Args:
            course_code: Code of the course to update
            updated_course: Updated course dictionary
            
        Returns:
            True if successful, False otherwise
        """
        courses = self.load_courses()
        
        for i, course in enumerate(courses):
            if course.get('code', '').upper() == course_code.upper():
                courses[i] = updated_course
                return self.save_courses(courses)
        
        logger.warning(f"Course {course_code} not found for update")
        return False
    
    def delete_course(self, course_code: str) -> bool:
        """
        Delete a course from the database.
        
        Args:
            course_code: Code of the course to delete
            
        Returns:
            True if successful, False otherwise
        """
        courses = self.load_courses()
        
        for i, course in enumerate(courses):
            if course.get('code', '').upper() == course_code.upper():
                del courses[i]
                return self.save_courses(courses)
        
        logger.warning(f"Course {course_code} not found for deletion")
        return False
    
    def get_courses_dataframe(self) -> pd.DataFrame:
        """
        Get courses as a pandas DataFrame for analysis.
        
        Returns:
            DataFrame containing course data
        """
        try:
            courses = self.load_courses()
            return pd.DataFrame(courses)
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            return pd.DataFrame()
    
    def _get_sample_courses(self) -> List[Dict[str, Any]]:
        """Get sample course data for initialization."""
        return [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming and computer science. Introduction to problem-solving, algorithm design, and programming in Python.",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "None",
                "instructor": "Dr. Smith",
                "schedule": "MWF 10:00-11:00 AM"
            },
            {
                "code": "CS201",
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures including arrays, linked lists, stacks, queues, trees, and graphs. Algorithm design and analysis.",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "CS101",
                "instructor": "Dr. Johnson",
                "schedule": "TTh 2:00-3:30 PM"
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks, and deep learning applications.",
                "credits": 3,
                "difficulty": 4,
                "category": "Major Electives",
                "semester": "Fall/Spring",
                "prerequisites": "CS201, MATH201",
                "instructor": "Dr. Chen",
                "schedule": "MWF 1:00-2:00 PM"
            },
            {
                "code": "CS302",
                "title": "Web Development",
                "description": "Full-stack web development using modern frameworks. HTML, CSS, JavaScript, React, Node.js, and database integration.",
                "credits": 3,
                "difficulty": 3,
                "category": "Major Electives",
                "semester": "Fall/Spring",
                "prerequisites": "CS101",
                "instructor": "Prof. Garcia",
                "schedule": "TTh 11:00-12:30 PM"
            },
            {
                "code": "CS303",
                "title": "Database Systems",
                "description": "Database design, SQL, relational algebra, normalization, transaction processing, and distributed databases.",
                "credits": 3,
                "difficulty": 3,
                "category": "Major Electives",
                "semester": "Fall/Spring",
                "prerequisites": "CS201",
                "instructor": "Dr. Williams",
                "schedule": "MWF 3:00-4:00 PM"
            },
            {
                "code": "MATH201",
                "title": "Calculus I",
                "description": "Differential calculus, limits, derivatives, applications to optimization, and introduction to integral calculus.",
                "credits": 4,
                "difficulty": 3,
                "category": "Math/Science",
                "semester": "Fall/Spring",
                "prerequisites": "Pre-calculus or placement test",
                "instructor": "Prof. Davis",
                "schedule": "MWF 9:00-10:00 AM, Th 9:00-10:00 AM"
            },
            {
                "code": "MATH202",
                "title": "Statistics",
                "description": "Probability theory, statistical inference, hypothesis testing, regression analysis, and data interpretation.",
                "credits": 3,
                "difficulty": 3,
                "category": "Math/Science",
                "semester": "Fall/Spring",
                "prerequisites": "MATH201",
                "instructor": "Dr. Brown",
                "schedule": "TTh 10:00-11:30 AM"
            },
            {
                "code": "ENG102",
                "title": "English Composition",
                "description": "Academic writing skills, critical thinking, research methods, and effective communication in various contexts.",
                "credits": 3,
                "difficulty": 2,
                "category": "General Education",
                "semester": "Fall/Spring",
                "prerequisites": "None",
                "instructor": "Prof. Taylor",
                "schedule": "MWF 11:00-12:00 PM"
            },
            {
                "code": "PHIL101",
                "title": "Introduction to Philosophy",
                "description": "Classical and contemporary philosophical problems, logic, ethics, metaphysics, and critical reasoning skills.",
                "credits": 3,
                "difficulty": 2,
                "category": "Humanities",
                "semester": "Fall/Spring",
                "prerequisites": "None",
                "instructor": "Dr. Wilson",
                "schedule": "TTh 1:00-2:30 PM"
            },
            {
                "code": "HIST201",
                "title": "World History",
                "description": "Survey of world civilizations, cultural developments, historical analysis methods, and global perspectives.",
                "credits": 3,
                "difficulty": 2,
                "category": "Humanities",
                "semester": "Fall/Spring",
                "prerequisites": "None",
                "instructor": "Prof. Martinez",
                "schedule": "MWF 2:00-3:00 PM"
            }
        ]
    
    def _get_sample_requirements(self) -> Dict[str, Any]:
        """Get sample graduation requirements for initialization."""
        return {
            "Computer Science": {
                "total_credits": 120,
                "categories": {
                    "Core Requirements": {
                        "credits": 24,
                        "courses": ["CS101", "CS201", "CS202", "CS301", "CS401", "CS402", "CS403", "CS404"]
                    },
                    "Major Electives": {
                        "credits": 18,
                        "courses": ["CS301", "CS302", "CS303", "CS304", "CS305", "CS306"]
                    },
                    "Math/Science": {
                        "credits": 20,
                        "courses": ["MATH201", "MATH202", "MATH203", "PHYS101", "PHYS102"]
                    },
                    "General Education": {
                        "credits": 30,
                        "courses": ["ENG101", "ENG102", "HIST101", "PHIL101", "ART101"]
                    },
                    "Free Electives": {
                        "credits": 28,
                        "courses": []
                    }
                }
            },
            "Engineering": {
                "total_credits": 128,
                "categories": {
                    "Core Requirements": {
                        "credits": 32,
                        "courses": ["ENGR101", "ENGR201", "ENGR301", "ENGR401"]
                    },
                    "Math/Science": {
                        "credits": 24,
                        "courses": ["MATH201", "MATH202", "MATH203", "PHYS201", "CHEM101"]
                    },
                    "General Education": {
                        "credits": 24,
                        "courses": ["ENG101", "ENG102", "HIST101", "ECON101"]
                    },
                    "Technical Electives": {
                        "credits": 24,
                        "courses": []
                    },
                    "Free Electives": {
                        "credits": 24,
                        "courses": []
                    }
                }
            }
        }


# Convenience functions for standalone usage
def load_courses(file_path: str = "data/courses.json") -> List[Dict[str, Any]]:
    """
    Load courses from JSON file (standalone function).
    
    Args:
        file_path: Path to courses JSON file
        
    Returns:
        List of course dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            courses = json.load(f)
        logger.info(f"Loaded {len(courses)} courses from {file_path}")
        return courses
    except FileNotFoundError:
        logger.error(f"Courses file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing courses JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading courses: {e}")
        return []


def save_courses(courses: List[Dict[str, Any]], file_path: str = "data/courses.json") -> bool:
    """
    Save courses to JSON file (standalone function).
    
    Args:
        courses: List of course dictionaries
        file_path: Path to save courses JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(courses, f, indent=2)
        logger.info(f"Saved {len(courses)} courses to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving courses: {e}")
        return False
