"""
Unit Tests for Data Manager Module

Tests for src/data_manager.py functionality including:
- Course data loading and validation
- Error handling for missing files
- Data structure validation
- Performance testing
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_manager import load_courses


class TestDataManager(unittest.TestCase):
    """Test cases for data manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_courses = [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Basic programming concepts",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "CS201",
                "title": "Data Structures",
                "description": "Advanced data structures",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "CS101"
            }
        ]
    
    def test_load_courses_success(self):
        """Test successful course loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_courses, f)
            temp_file = f.name
        
        try:
            # Mock the default file path
            with patch('src.data_manager.Path') as mock_path:
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.__str__ = lambda x: temp_file
                
                courses = load_courses()
                
                self.assertEqual(len(courses), 2)
                self.assertEqual(courses[0]["code"], "CS101")
                self.assertEqual(courses[1]["code"], "CS201")
        finally:
            os.unlink(temp_file)
    
    def test_load_courses_custom_path(self):
        """Test loading courses from custom path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_courses, f)
            temp_file = f.name
        
        try:
            courses = load_courses(temp_file)
            self.assertEqual(len(courses), 2)
            self.assertEqual(courses[0]["title"], "Introduction to Computer Science")
        finally:
            os.unlink(temp_file)
    
    def test_load_courses_file_not_found(self):
        """Test handling of missing course file"""
        with self.assertRaises(FileNotFoundError):
            load_courses("nonexistent_file.json")
    
    def test_load_courses_invalid_json(self):
        """Test handling of invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_file = f.name
        
        try:
            with self.assertRaises(json.JSONDecodeError):
                load_courses(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_courses_empty_file(self):
        """Test handling of empty course file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_file = f.name
        
        try:
            courses = load_courses(temp_file)
            self.assertEqual(len(courses), 0)
            self.assertIsInstance(courses, list)
        finally:
            os.unlink(temp_file)
    
    def test_course_data_structure(self):
        """Test course data structure validation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_courses, f)
            temp_file = f.name
        
        try:
            courses = load_courses(temp_file)
            
            # Check required fields
            required_fields = ["code", "title", "description", "credits", "difficulty"]
            for course in courses:
                for field in required_fields:
                    self.assertIn(field, course)
                    self.assertIsNotNone(course[field])
                
                # Check data types
                self.assertIsInstance(course["code"], str)
                self.assertIsInstance(course["title"], str)
                self.assertIsInstance(course["credits"], int)
                self.assertIsInstance(course["difficulty"], int)
                
        finally:
            os.unlink(temp_file)
    
    def test_course_prerequisites_format(self):
        """Test prerequisites field formatting"""
        courses_with_prereqs = [
            {"code": "CS101", "title": "Intro", "description": "Basic", 
             "credits": 3, "difficulty": 2, "prerequisites": "None"},
            {"code": "CS201", "title": "Data Structures", "description": "Advanced", 
             "credits": 4, "difficulty": 4, "prerequisites": "CS101"},
            {"code": "CS301", "title": "ML", "description": "Machine Learning", 
             "credits": 3, "difficulty": 4, "prerequisites": "CS201, MATH201"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(courses_with_prereqs, f)
            temp_file = f.name
        
        try:
            courses = load_courses(temp_file)
            
            # Test different prerequisite formats
            self.assertEqual(courses[0]["prerequisites"], "None")
            self.assertEqual(courses[1]["prerequisites"], "CS101")
            self.assertIn("CS201", courses[2]["prerequisites"])
            self.assertIn("MATH201", courses[2]["prerequisites"])
            
        finally:
            os.unlink(temp_file)
    
    def test_large_course_dataset(self):
        """Test performance with larger dataset"""
        # Create a larger dataset
        large_dataset = []
        for i in range(100):
            course = {
                "code": f"CS{i:03d}",
                "title": f"Course {i}",
                "description": f"Description for course {i}",
                "credits": 3 + (i % 3),
                "difficulty": 1 + (i % 5),
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "None" if i == 0 else f"CS{i-1:03d}"
            }
            large_dataset.append(course)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_dataset, f)
            temp_file = f.name
        
        try:
            import time
            start_time = time.time()
            courses = load_courses(temp_file)
            load_time = time.time() - start_time
            
            self.assertEqual(len(courses), 100)
            self.assertLess(load_time, 1.0)  # Should load in less than 1 second
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    unittest.main()
