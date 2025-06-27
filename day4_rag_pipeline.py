"""
Day 4: Complete RAG (Retrieval-Augmented Generation) Pipeline

This module implements the Day 4 requirements:
✅ Implement retrieval → context injection → LLM response pipeline
✅ Handle multiple retrieved documents
✅ Build pipeline: input → embed → retrieve → inject into prompt → LLM → structured response
✅ Add support for fallback if vector similarity is low

Author: Course Recommendation System
Date: Day 4 Implementation
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# Import our existing components
from day3_embedding_search import EmbeddingBasedCourseSearch
from src.data_manager import load_courses

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for RAG responses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FALLBACK = "fallback"


@dataclass
class RAGResponse:
    """Structured response from the RAG pipeline"""
    response: str
    confidence: ConfidenceLevel
    retrieved_courses: List[Dict[str, Any]]
    similarity_scores: List[float]
    context_used: str
    reasoning: str
    fallback_triggered: bool = False


class Day4RAGPipeline:
    """
    Day 4: Complete RAG Pipeline Implementation
    
    This class implements the full RAG workflow:
    1. Input query processing
    2. Query embedding
    3. Vector similarity search
    4. Context retrieval and injection
    5. LLM prompt engineering
    6. Structured response generation
    7. Fallback handling for low similarity
    """
    
    def __init__(self, api_key: Optional[str] = None, similarity_threshold: float = 0.3):
        """
        Initialize the RAG pipeline.
        
        Args:
            api_key: OpenAI API key
            similarity_threshold: Minimum similarity score for confidence
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.similarity_threshold = similarity_threshold
        
        # Initialize embedding search system
        self.embedding_search = EmbeddingBasedCourseSearch(api_key=self.api_key)
        
        # Load and embed courses
        self.courses = load_courses("data/courses.json")
        self.embedding_search.embed_courses(self.courses)
        
        logger.info(f"Initialized Day4RAGPipeline with {len(self.courses)} courses")
    
    def _determine_confidence(self, similarities: List[float]) -> ConfidenceLevel:
        """
        Determine confidence level based on similarity scores.
        
        Args:
            similarities: List of similarity scores
            
        Returns:
            Confidence level
        """
        if not similarities:
            return ConfidenceLevel.FALLBACK
        
        max_similarity = max(similarities)
        avg_similarity = sum(similarities) / len(similarities)
        
        if max_similarity >= 0.6 and avg_similarity >= 0.4:
            return ConfidenceLevel.HIGH
        elif max_similarity >= 0.4 and avg_similarity >= 0.3:
            return ConfidenceLevel.MEDIUM
        elif max_similarity >= self.similarity_threshold:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.FALLBACK
    
    def _build_context(self, retrieved_courses: List[Tuple[Dict[str, Any], float]], max_courses: int = 5) -> str:
        """
        ✅ Day 4 Requirement: Handle multiple retrieved documents
        
        Build context string from retrieved courses.
        
        Args:
            retrieved_courses: List of (course, similarity) tuples
            max_courses: Maximum number of courses to include
            
        Returns:
            Formatted context string
        """
        if not retrieved_courses:
            return "No relevant courses found."
        
        context_parts = ["RELEVANT COURSES FOUND:"]
        
        for i, (course, similarity) in enumerate(retrieved_courses[:max_courses], 1):
            context_parts.append(f"""
{i}. {course['title']} ({course['code']})
   - Description: {course['description']}
   - Credits: {course['credits']} | Difficulty: {course['difficulty']}/5
   - Category: {course['category']} | Semester: {course['semester']}
   - Prerequisites: {course.get('prerequisites', 'None')}
   - Relevance Score: {similarity:.3f}
""")
        
        return "\\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str, confidence: ConfidenceLevel) -> str:
        """
        ✅ Day 4 Requirement: Context injection into LLM prompt
        
        Create a sophisticated RAG prompt with context injection.
        
        Args:
            query: User query
            context: Retrieved context
            confidence: Confidence level
            
        Returns:
            Formatted prompt for LLM
        """
        base_prompt = f"""You are an expert course advisor for a computer science program. Your task is to provide personalized course recommendations based on student interests and retrieved course information.

STUDENT QUERY: "{query}"

RETRIEVED COURSE CONTEXT:
{context}

CONFIDENCE LEVEL: {confidence.value}

INSTRUCTIONS:
1. Analyze the student's query to understand their interests, goals, and preferences
2. Use the retrieved course information to make informed recommendations
3. Explain WHY each course is relevant to their interests
4. Consider prerequisites, difficulty levels, and course categories
5. Provide specific, actionable advice
6. If confidence is low, acknowledge limitations and suggest broader exploration

RESPONSE FORMAT:
- Start with a brief analysis of the student's interests
- Provide 3-5 specific course recommendations with detailed explanations
- Include practical advice about prerequisites and planning
- End with additional suggestions or next steps

RESPONSE:"""

        if confidence == ConfidenceLevel.FALLBACK:
            base_prompt += """
            
NOTE: The similarity search returned limited relevant results. Please provide general guidance and suggest the student:
1. Refine their query with more specific interests
2. Explore course categories that might align with their goals
3. Consider speaking with an academic advisor for personalized guidance"""
        
        return base_prompt
    
    def _generate_llm_response(self, prompt: str) -> str:
        """
        Generate response using OpenAI LLM.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            LLM response
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert academic advisor specializing in computer science course recommendations. Provide helpful, specific, and encouraging advice to students."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error generating a response. Please try again or contact support. Error: {str(e)}"
    
    def _generate_reasoning(self, query: str, confidence: ConfidenceLevel, similarities: List[float]) -> str:
        """
        Generate reasoning explanation for the response.
        
        Args:
            query: Original query
            confidence: Confidence level
            similarities: Similarity scores
            
        Returns:
            Reasoning explanation
        """
        reasoning_parts = [
            f"Query Analysis: Processed student interest in '{query}'",
            f"Vector Search: Found {len(similarities)} relevant courses",
        ]
        
        if similarities:
            reasoning_parts.append(f"Similarity Range: {min(similarities):.3f} - {max(similarities):.3f}")
            reasoning_parts.append(f"Average Similarity: {sum(similarities)/len(similarities):.3f}")
        
        reasoning_parts.append(f"Confidence Level: {confidence.value} ({self._get_confidence_explanation(confidence)})")
        
        return " | ".join(reasoning_parts)
    
    def _get_confidence_explanation(self, confidence: ConfidenceLevel) -> str:
        """Get explanation for confidence level"""
        explanations = {
            ConfidenceLevel.HIGH: "Strong semantic match with multiple relevant courses",
            ConfidenceLevel.MEDIUM: "Good semantic match with some relevant courses", 
            ConfidenceLevel.LOW: "Moderate semantic match, recommendations may be broad",
            ConfidenceLevel.FALLBACK: "Limited semantic match, providing general guidance"
        }
        return explanations.get(confidence, "Unknown confidence level")
    
    def process_query(self, query: str, top_k: int = 5) -> RAGResponse:
        """
        ✅ Day 4 Requirement: Complete RAG pipeline
        
        Process a student query through the complete RAG pipeline:
        input → embed → retrieve → inject into prompt → LLM → structured response
        
        Args:
            query: Student query about course interests
            top_k: Number of courses to retrieve
            
        Returns:
            Structured RAG response
        """
        logger.info(f"Processing RAG query: '{query}'")
        
        try:
            # Step 1: Embed the query
            logger.info("Step 1: Embedding query...")
            
            # Step 2: Retrieve similar courses
            logger.info("Step 2: Retrieving similar courses...")
            retrieved_results = self.embedding_search.search_courses_by_interests(query, top_k=top_k)
            
            # Extract courses and similarities from the results
            retrieved_courses = []
            similarities = []
            
            for result in retrieved_results:
                course_copy = result.copy()
                similarity = course_copy.pop('similarity_score', 0.0)
                course_copy.pop('rank', None)  # Remove rank if present
                
                retrieved_courses.append((course_copy, similarity))
                similarities.append(similarity)
            
            # Extract courses and similarities for further processing
            courses = [course for course, similarity in retrieved_courses]
            
            # Step 3: Determine confidence level
            confidence = self._determine_confidence(similarities)
            logger.info(f"Step 3: Confidence level determined: {confidence.value}")
            
            # Step 4: Build context from retrieved documents
            logger.info("Step 4: Building context from retrieved documents...")
            context = self._build_context(retrieved_courses, max_courses=top_k)
            
            # Step 5: Create RAG prompt with context injection
            logger.info("Step 5: Creating RAG prompt with context injection...")
            prompt = self._create_rag_prompt(query, context, confidence)
            
            # Step 6: Generate LLM response
            logger.info("Step 6: Generating LLM response...")
            llm_response = self._generate_llm_response(prompt)
            
            # Step 7: Generate reasoning
            reasoning = self._generate_reasoning(query, confidence, similarities)
            
            # Step 8: Create structured response
            response = RAGResponse(
                response=llm_response,
                confidence=confidence,
                retrieved_courses=courses,
                similarity_scores=similarities,
                context_used=context,
                reasoning=reasoning,
                fallback_triggered=(confidence == ConfidenceLevel.FALLBACK)
            )
            
            logger.info(f"✅ RAG pipeline completed successfully with {confidence.value} confidence")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            
            # Fallback response
            fallback_response = self._generate_fallback_response(query, str(e))
            return RAGResponse(
                response=fallback_response,
                confidence=ConfidenceLevel.FALLBACK,
                retrieved_courses=[],
                similarity_scores=[],
                context_used="Error occurred during retrieval",
                reasoning=f"Error in pipeline: {str(e)}",
                fallback_triggered=True
            )
    
    def _generate_fallback_response(self, query: str, error: str) -> str:
        """
        ✅ Day 4 Requirement: Fallback if vector similarity is low
        
        Generate fallback response when similarity is too low or errors occur.
        
        Args:
            query: Original query
            error: Error message if applicable
            
        Returns:
            Fallback response
        """
        return f"""I understand you're interested in courses related to "{query}". While I couldn't find specific course matches with high confidence, I can offer some general guidance:

**General Recommendations:**
1. **Explore Core Requirements**: Start with fundamental courses like Introduction to Computer Science and Data Structures
2. **Check Prerequisites**: Many advanced courses require foundational knowledge
3. **Consider Your Background**: Think about your current skill level and experience
4. **Talk to Advisors**: Academic advisors can provide personalized course planning

**Next Steps:**
- Try refining your query with more specific interests (e.g., "machine learning algorithms" instead of "AI")
- Browse the full course catalog to discover new areas of interest
- Consider what career goals you want to achieve through your coursework

**Popular Course Categories:**
- Core Requirements: Fundamental programming and computer science concepts
- Major Electives: Specialized topics like AI, web development, databases
- Math/Science: Supporting mathematics and science courses

Would you like to try a more specific query or ask about particular course categories?"""


def demonstrate_rag_pipeline():
    """
    Demonstrate the Day 4 RAG pipeline with various queries
    """
    print("🎯 Day 4: RAG Pipeline Demonstration")
    print("="*60)
    
    # Initialize pipeline
    print("1️⃣ Initializing RAG Pipeline...")
    pipeline = Day4RAGPipeline()
    print("   ✅ Pipeline initialized")
    
    # Test queries with different expected confidence levels
    test_queries = [
        "I'm passionate about artificial intelligence and machine learning",
        "I want to learn web development and modern frameworks", 
        "I'm interested in algorithms and mathematical optimization",
        "I like databases and data management systems",
        "I want to study quantum computing and blockchain"  # This should trigger fallback
    ]
    
    for i, query in enumerate(test_queries, 2):
        print(f"\\n{i}️⃣ Testing Query: '{query}'")
        print("-" * 50)
        
        response = pipeline.process_query(query)
        
        print(f"   📊 Confidence: {response.confidence.value}")
        print(f"   📈 Similarity Scores: {[f'{s:.3f}' for s in response.similarity_scores[:3]]}")
        print(f"   📚 Retrieved Courses: {len(response.retrieved_courses)}")
        print(f"   🔄 Fallback Triggered: {response.fallback_triggered}")
        print(f"   🧠 Reasoning: {response.reasoning}")
        print(f"\\n   💬 Response Preview:")
        print(f"   {response.response[:200]}...")
    
    print(f"\\n✅ Day 4 RAG Pipeline demonstration complete!")


if __name__ == "__main__":
    demonstrate_rag_pipeline()
