"""
Day 3: Embedding-Based Course Search Module

This module implements the Day 3 requirements:
✅ Use text-embedding-3-small to embed course descriptions
✅ Use FAISS to index and retrieve relevant courses
✅ Write a Python module that embeds courses and student queries
✅ Return top 5 most similar courses

Author: Course Recommendation System
Date: Day 3 Implementation
"""

import os
import json
import numpy as np
import faiss
import logging
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingBasedCourseSearch:
    """
    Day 3: Embedding-based course search using OpenAI embeddings and FAISS.
    
    This class implements all Day 3 requirements:
    - Uses text-embedding-3-small for course and query embeddings
    - Uses FAISS for efficient vector indexing and similarity search
    - Provides methods to embed courses, embed queries, and find similar courses
    """
    
    def __init__(self, api_key: Optional[str] = None, embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the embedding-based course search system.
        
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            embedding_model: OpenAI embedding model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.embedding_model = embedding_model
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        
        # FAISS index and course storage
        self.faiss_index = None
        self.courses = []  # Store original course data
        self.course_embeddings = []  # Store embeddings
        
        logger.info(f"Initialized EmbeddingBasedCourseSearch with model: {embedding_model}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        ✅ Day 3 Requirement: Use text-embedding-3-small to embed text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dimension, dtype=np.float32)
    
    def embed_courses(self, courses: List[Dict[str, Any]]) -> None:
        """
        ✅ Day 3 Requirement: Embed course descriptions using text-embedding-3-small.
        
        Args:
            courses: List of course dictionaries with descriptions
        """
        logger.info(f"Embedding {len(courses)} courses using {self.embedding_model}...")
        
        self.courses = courses
        self.course_embeddings = []
        
        for i, course in enumerate(courses):
            # Create comprehensive text for embedding
            course_text = self._create_course_text(course)
            
            # Get embedding from OpenAI
            embedding = self.embed_text(course_text)
            self.course_embeddings.append(embedding)
            
            if (i + 1) % 5 == 0:
                logger.info(f"Embedded {i + 1}/{len(courses)} courses")
        
        # Convert to numpy array
        self.course_embeddings = np.vstack(self.course_embeddings)
        
        # Build FAISS index
        self._build_faiss_index()
        
        logger.info(f"✅ Successfully embedded {len(courses)} courses")
    
    def _create_course_text(self, course: Dict[str, Any]) -> str:
        """
        Create comprehensive text representation of a course for embedding.
        
        Args:
            course: Course dictionary
            
        Returns:
            Combined text representation
        """
        text_parts = []
        
        # Add title
        if course.get('title'):
            text_parts.append(f"Course: {course['title']}")
        
        # Add description (most important)
        if course.get('description'):
            text_parts.append(f"Description: {course['description']}")
        
        # Add category
        if course.get('category'):
            text_parts.append(f"Category: {course['category']}")
        
        # Add prerequisites for context
        if course.get('prerequisites') and course['prerequisites'] != 'None':
            text_parts.append(f"Prerequisites: {course['prerequisites']}")
        
        return " ".join(text_parts)
    
    def _build_faiss_index(self) -> None:
        """
        ✅ Day 3 Requirement: Use FAISS to index course embeddings.
        """
        if len(self.course_embeddings) == 0:
            logger.warning("No course embeddings to index")
            return
        
        # Create FAISS index (using cosine similarity via inner product)
        # Normalize embeddings for cosine similarity
        normalized_embeddings = self.course_embeddings / np.linalg.norm(
            self.course_embeddings, axis=1, keepdims=True
        )
        
        # Create index
        self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner Product for cosine similarity
        self.faiss_index.add(normalized_embeddings)
        
        logger.info(f"✅ Built FAISS index with {self.faiss_index.ntotal} course embeddings")
    
    def embed_student_query(self, query: str) -> np.ndarray:
        """
        ✅ Day 3 Requirement: Embed a student query (e.g., "I like psychology and AI").
        
        Args:
            query: Student query string
            
        Returns:
            Query embedding as numpy array
        """
        logger.info(f"Embedding student query: '{query}'")
        
        # Create more descriptive query text
        enhanced_query = f"Student interests: {query}. Looking for relevant courses."
        
        embedding = self.embed_text(enhanced_query)
        
        # Normalize for cosine similarity
        normalized_embedding = embedding / np.linalg.norm(embedding)
        
        return normalized_embedding
    
    def find_similar_courses(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        ✅ Day 3 Requirement: Return top 5 most similar courses.
        
        Args:
            query: Student query (e.g., "I like psychology and AI")
            top_k: Number of similar courses to return (default 5)
            
        Returns:
            List of top-k most similar courses with similarity scores
        """
        if self.faiss_index is None:
            logger.error("FAISS index not built. Please embed courses first.")
            return []
        
        # Embed the query
        query_embedding = self.embed_student_query(query)
        
        # Search FAISS index
        similarities, indices = self.faiss_index.search(
            query_embedding.reshape(1, -1), top_k
        )
        
        # Prepare results
        results = []
        for i, (similarity, course_idx) in enumerate(zip(similarities[0], indices[0])):
            if course_idx < len(self.courses):
                course = self.courses[course_idx].copy()
                course['similarity_score'] = float(similarity)
                course['rank'] = i + 1
                results.append(course)
        
        logger.info(f"✅ Found {len(results)} similar courses for query: '{query}'")
        
        return results
    
    def search_courses_by_interests(self, interests: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Main search method that implements the complete Day 3 workflow.
        
        Args:
            interests: Student interests (e.g., "I like psychology and AI")
            top_k: Number of courses to return
            
        Returns:
            Top-k most similar courses
        """
        return self.find_similar_courses(interests, top_k)
    
    def save_embeddings(self, filepath: str) -> None:
        """
        Save course embeddings to disk for reuse.
        
        Args:
            filepath: Path to save embeddings
        """
        if len(self.course_embeddings) == 0:
            logger.warning("No embeddings to save")
            return
        
        data = {
            'embeddings': self.course_embeddings.tolist(),
            'courses': self.courses,
            'embedding_model': self.embedding_model
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        logger.info(f"Saved embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str) -> None:
        """
        Load pre-computed embeddings from disk.
        
        Args:
            filepath: Path to load embeddings from
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.course_embeddings = np.array(data['embeddings'], dtype=np.float32)
            self.courses = data['courses']
            self.embedding_model = data.get('embedding_model', 'text-embedding-3-small')
            
            self._build_faiss_index()
            
            logger.info(f"Loaded embeddings from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embedded courses.
        
        Returns:
            Dictionary with embedding statistics
        """
        if len(self.course_embeddings) == 0:
            return {"status": "No embeddings available"}
        
        return {
            "num_courses": len(self.courses),
            "embedding_dimension": self.embedding_dimension,
            "embedding_model": self.embedding_model,
            "faiss_index_size": self.faiss_index.ntotal if self.faiss_index else 0,
            "average_embedding_norm": float(np.mean(np.linalg.norm(self.course_embeddings, axis=1)))
        }


def demo_day3_requirements():
    """
    Demonstrate all Day 3 requirements in action.
    """
    print("🎯 Day 3: Embedding-Based Course Search Demo")
    print("=" * 50)
    
    try:
        # Initialize the search system
        search_system = EmbeddingBasedCourseSearch()
        print("✅ Initialized embedding-based course search system")
        
        # Load course data
        from data_manager import DataManager
        data_manager = DataManager()
        courses = data_manager.load_courses()
        
        print(f"📚 Loaded {len(courses)} courses")
        
        # ✅ Day 3 Requirement 1: Embed course descriptions
        print("\n🔄 Embedding course descriptions with text-embedding-3-small...")
        search_system.embed_courses(courses)
        
        # Show embedding stats
        stats = search_system.get_embedding_stats()
        print(f"✅ Embedded {stats['num_courses']} courses")
        print(f"   Model: {stats['embedding_model']}")
        print(f"   Dimension: {stats['embedding_dimension']}")
        print(f"   FAISS Index Size: {stats['faiss_index_size']}")
        
        # ✅ Day 3 Requirement 2: Test various student queries
        test_queries = [
            "I like psychology and AI",
            "I'm interested in programming and web development", 
            "I want to learn about databases and data science",
            "I enjoy mathematics and algorithms",
            "I like computer networks and security"
        ]
        
        print("\n🔍 Testing student query embeddings and similarity search:")
        print("-" * 50)
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            
            # ✅ Day 3 Requirement 3: Return top 5 most similar courses
            similar_courses = search_system.search_courses_by_interests(query, top_k=5)
            
            print(f"🎯 Top {len(similar_courses)} most similar courses:")
            
            for course in similar_courses:
                print(f"   {course['rank']}. {course['title']} ({course['code']})")
                print(f"      Similarity: {course['similarity_score']:.3f}")
                print(f"      Category: {course['category']}")
                print(f"      Description: {course['description'][:80]}...")
                print()
        
        print("✅ All Day 3 requirements successfully demonstrated!")
        
        # Save embeddings for reuse
        search_system.save_embeddings("day3_embeddings.json")
        print("💾 Saved embeddings for future use")
        
        return search_system
        
    except Exception as e:
        print(f"❌ Error in Day 3 demo: {e}")
        return None


def main():
    """
    Main function to run Day 3 demonstration.
    """
    # Add src to path for imports
    import sys
    sys.path.append('./src')
    
    # Run the demo
    search_system = demo_day3_requirements()
    
    if search_system:
        print("\n" + "=" * 50)
        print("🎉 Day 3 Implementation Complete!")
        print("=" * 50)
        print("\nDay 3 Achievements:")
        print("✅ Used text-embedding-3-small for course embeddings")
        print("✅ Used FAISS for efficient vector indexing")
        print("✅ Implemented student query embedding")
        print("✅ Return top 5 most similar courses")
        print("✅ Full Python module with comprehensive functionality")
        
        # Interactive mode
        print("\n💬 Interactive Mode - Test your own queries!")
        print("Enter student interests (type 'quit' to exit):")
        
        while True:
            user_query = input("\n🎓 Student interests: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_query:
                print(f"\n🔍 Searching for courses similar to: '{user_query}'")
                results = search_system.search_courses_by_interests(user_query, top_k=5)
                
                print(f"\n🎯 Top {len(results)} recommendations:")
                for course in results:
                    print(f"   {course['rank']}. {course['title']} - Similarity: {course['similarity_score']:.3f}")
            else:
                print("Please enter valid student interests.")
        
        print("\n👋 Day 3 Demo completed successfully!")


if __name__ == "__main__":
    main()
