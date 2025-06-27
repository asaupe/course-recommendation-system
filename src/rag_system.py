"""
RAG System Module

Implements Retrieval-Augmented Generation for course information using ChromaDB.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    RAG (Retrieval-Augmented Generation) system for course information.
    Uses ChromaDB for vector storage and similarity search.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the RAG system.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="courses",
                metadata={"description": "Course information for recommendations"}
            )
            logger.info(f"Initialized RAG system with persist directory: {self.persist_directory}")
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB: {e}. Using fallback implementation.")
            self.client = None
            self.collection = None
            self._courses_data = []  # Fallback storage
    
    def add_courses(self, courses: List[Dict[str, Any]]) -> None:
        """
        Add courses to the vector database.
        
        Args:
            courses: List of course dictionaries
        """
        if not courses:
            return
            
        try:
            if self.collection is not None:
                # Prepare data for ChromaDB
                documents = []
                metadatas = []
                ids = []
                
                for course in courses:
                    # Create searchable text from course information
                    doc_text = f"{course.get('title', '')} {course.get('description', '')} {course.get('category', '')}"
                    documents.append(doc_text)
                    
                    # Store metadata
                    metadata = {
                        "code": course.get('code', ''),
                        "title": course.get('title', ''),
                        "category": course.get('category', ''),
                        "credits": str(course.get('credits', 0)),
                        "difficulty": str(course.get('difficulty', 0))
                    }
                    metadatas.append(metadata)
                    ids.append(course.get('code', f"course_{len(ids)}"))
                
                # Add to collection
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(courses)} courses to vector database")
            else:
                # Fallback: store in memory
                self._courses_data.extend(courses)
                logger.info(f"Added {len(courses)} courses to fallback storage")
                
        except Exception as e:
            logger.error(f"Error adding courses to RAG system: {e}")
            # Fallback to in-memory storage
            if not hasattr(self, '_courses_data'):
                self._courses_data = []
            self._courses_data.extend(courses)
    
    def search_courses(
        self, 
        query: str, 
        categories: Optional[List[str]] = None, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant courses based on query and filters.
        
        Args:
            query: Search query string
            categories: Optional list of categories to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant course dictionaries
        """
        try:
            if self.collection is not None:
                return self._search_with_chromadb(query, categories, max_results)
            else:
                return self._search_fallback(query, categories, max_results)
        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            return self._search_fallback(query, categories, max_results)
    
    def _search_with_chromadb(
        self, 
        query: str, 
        categories: Optional[List[str]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using ChromaDB vector similarity."""
        try:
            # Prepare where clause for category filtering
            where_clause = None
            if categories:
                where_clause = {"category": {"$in": categories}}
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                where=where_clause
            )
            
            # Convert results to course dictionaries
            courses = []
            for i, metadata in enumerate(results['metadatas'][0]):
                course = {
                    'code': metadata.get('code', ''),
                    'title': metadata.get('title', ''),
                    'description': results['documents'][0][i] if i < len(results['documents'][0]) else '',
                    'category': metadata.get('category', ''),
                    'credits': int(metadata.get('credits', 0)),
                    'difficulty': int(metadata.get('difficulty', 0)),
                    'semester': 'Fall/Spring',  # Default value
                    'prerequisites': 'Check with advisor'  # Default value
                }
                courses.append(course)
            
            return courses
            
        except Exception as e:
            logger.error(f"ChromaDB search error: {e}")
            return self._search_fallback(query, categories, max_results)
    
    def _search_fallback(
        self, 
        query: str, 
        categories: Optional[List[str]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Fallback search using simple text matching."""
        if not hasattr(self, '_courses_data'):
            self._courses_data = self._get_sample_courses()
        
        results = []
        query_lower = query.lower()
        
        for course in self._courses_data:
            # Check category filter
            if categories and course.get('category') not in categories:
                continue
            
            # Simple text matching
            searchable_text = f"{course.get('title', '')} {course.get('description', '')}".lower()
            if any(word in searchable_text for word in query_lower.split()):
                results.append(course.copy())
            
            if len(results) >= max_results:
                break
        
        # If no matches, return all courses (up to max_results)
        if not results:
            filtered_courses = [
                course for course in self._courses_data
                if not categories or course.get('category') in categories
            ]
            results = filtered_courses[:max_results]
        
        return results
    
    def _get_sample_courses(self) -> List[Dict[str, Any]]:
        """Generate sample courses for demonstration."""
        return [
            {
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Fundamental concepts of programming, algorithms, and data structures. Learn Python programming and computational thinking.",
                "credits": 3,
                "difficulty": 2,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "CS201",
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures, algorithm design and analysis. Covers trees, graphs, sorting, and searching algorithms.",
                "credits": 4,
                "difficulty": 4,
                "category": "Core Requirements",
                "semester": "Fall/Spring",
                "prerequisites": "CS101"
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks.",
                "credits": 3,
                "difficulty": 4,
                "category": "Major Electives",
                "semester": "Fall/Spring",
                "prerequisites": "CS201, MATH201"
            },
            {
                "code": "CS302",
                "title": "Web Development",
                "description": "Full-stack web development using modern frameworks. HTML, CSS, JavaScript, React, and backend development.",
                "credits": 3,
                "difficulty": 3,
                "category": "Major Electives",
                "semester": "Fall/Spring",
                "prerequisites": "CS101"
            },
            {
                "code": "MATH201",
                "title": "Calculus I",
                "description": "Differential calculus, limits, derivatives, and applications to real-world problems.",
                "credits": 4,
                "difficulty": 3,
                "category": "Math/Science",
                "semester": "Fall/Spring",
                "prerequisites": "Pre-calculus"
            },
            {
                "code": "MATH202",
                "title": "Statistics",
                "description": "Probability theory, statistical inference, hypothesis testing, and data analysis techniques.",
                "credits": 3,
                "difficulty": 3,
                "category": "Math/Science",
                "semester": "Fall/Spring",
                "prerequisites": "MATH201"
            },
            {
                "code": "ENG102",
                "title": "English Composition",
                "description": "Academic writing, critical thinking, research methods, and communication skills.",
                "credits": 3,
                "difficulty": 2,
                "category": "General Education",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "PHIL101",
                "title": "Introduction to Philosophy",
                "description": "Classical and contemporary philosophical problems, logic, ethics, and critical reasoning.",
                "credits": 3,
                "difficulty": 2,
                "category": "Humanities",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "HIST201",
                "title": "World History",
                "description": "Survey of world civilizations, cultural developments, and historical analysis methods.",
                "credits": 3,
                "difficulty": 2,
                "category": "Humanities",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            },
            {
                "code": "BUS101",
                "title": "Introduction to Business",
                "description": "Fundamentals of business operations, management principles, and entrepreneurship.",
                "credits": 3,
                "difficulty": 2,
                "category": "General Education",
                "semester": "Fall/Spring",
                "prerequisites": "None"
            }
        ]
    
    def get_course_count(self) -> int:
        """Get the number of courses in the system."""
        try:
            if self.collection is not None:
                return self.collection.count()
            else:
                return len(getattr(self, '_courses_data', []))
        except Exception:
            return 0
