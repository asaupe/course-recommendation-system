"""
Day 6: Streamlit Frontend for Course Recommendation System

This module implements the Day 6 requirements:
✅ Student enters interests/goals
✅ System returns course list with explanations
✅ Option to refine response (e.g., "I prefer online courses")
✅ Bonus: Allow user feedback (thumbs up/down)

Features:
- Interactive course recommendation interface
- Real-time response generation
- Query refinement and iteration
- User feedback collection
- Modern, responsive UI
- Session state management

Author: Course Recommendation System
Date: Day 6 Implementation
"""

import streamlit as st
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# Import our existing components
from day5_guardrails import Day5GuardedRAGPipeline, ValidatedRecommendationResponse
from src.data_manager import load_courses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🎓 AI Course Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .course-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .feedback-section {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    .refinement-tips {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitCourseRecommender:
    """Streamlit frontend for the course recommendation system"""
    
    def __init__(self):
        """Initialize the Streamlit app"""
        self.initialize_session_state()
        self.load_pipeline()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'recommendations' not in st.session_state:
            st.session_state.recommendations = None
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'feedback_data' not in st.session_state:
            st.session_state.feedback_data = []
        if 'pipeline_loaded' not in st.session_state:
            st.session_state.pipeline_loaded = False
        if 'refined_queries' not in st.session_state:
            st.session_state.refined_queries = []
    
    def load_pipeline(self):
        """Load the RAG pipeline with caching"""
        if not st.session_state.pipeline_loaded:
            with st.spinner("🤖 Loading AI Course Recommendation System..."):
                try:
                    self.pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
                    self.courses = load_courses()
                    st.session_state.pipeline_loaded = True
                    logger.info("Pipeline loaded successfully")
                except Exception as e:
                    st.error(f"Error loading pipeline: {e}")
                    logger.error(f"Pipeline loading error: {e}")
                    return False
        else:
            self.pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
            self.courses = load_courses()
        return True
    
    def render_header(self):
        """Render the main application header"""
        st.markdown('<h1 class="main-header">🎓 AI Course Recommender</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: #666;">
                Get personalized course recommendations powered by AI and RAG technology
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with app information and controls"""
        with st.sidebar:
            st.header("📋 How It Works")
            st.markdown("""
            1. **Enter your interests** and academic goals
            2. **Get AI-powered recommendations** based on course data
            3. **Refine your search** with additional preferences
            4. **Provide feedback** to improve recommendations
            """)
            
            st.header("📊 System Status")
            if st.session_state.pipeline_loaded:
                st.success("✅ AI System Ready")
                st.info(f"📚 {len(self.courses)} courses available")
            else:
                st.warning("⏳ Loading AI System...")
            
            if st.session_state.query_history:
                st.header("📝 Query History")
                for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                    st.text(f"{i}. {query[:50]}...")
            
            st.header("⚙️ Settings")
            confidence_threshold = st.slider(
                "Confidence Threshold", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.6, 
                step=0.1,
                help="Minimum confidence for recommendations"
            )
            
            show_debug = st.checkbox("Show Debug Info", value=False)
            
            return confidence_threshold, show_debug
    
    def render_query_input(self):
        """Render the main query input section"""
        st.header("🔍 What courses are you looking for?")
        
        # Example queries for inspiration
        with st.expander("💡 Need inspiration? Try these examples:"):
            example_queries = [
                "I want to learn machine learning and AI",
                "I need courses for web development career",
                "I'm interested in data science and statistics",
                "I want to study algorithms and programming",
                "I prefer hands-on courses in technology",
                "I need beginner-friendly computer science courses"
            ]
            
            cols = st.columns(2)
            for i, query in enumerate(example_queries):
                col = cols[i % 2]
                if col.button(f"💭 {query}", key=f"example_{i}"):
                    return query
        
        # Main query input
        query = st.text_area(
            "Describe your interests, goals, and preferences:",
            placeholder="Example: I want to learn programming and data analysis. I prefer beginner-friendly courses with practical projects...",
            height=100,
            key="main_query"
        )
        
        # Additional preferences
        col1, col2 = st.columns(2)
        
        with col1:
            difficulty_pref = st.selectbox(
                "Preferred Difficulty",
                ["Any", "Beginner (1-2)", "Intermediate (3-4)", "Advanced (5)"],
                help="Filter courses by difficulty level"
            )
        
        with col2:
            category_pref = st.selectbox(
                "Preferred Category",
                ["Any", "Core Requirements", "Electives", "Specialization", "Capstone"],
                help="Filter courses by category"
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            num_recommendations = st.slider(
                "Number of recommendations", 
                min_value=1, 
                max_value=10, 
                value=5
            )
            
            include_prerequisites = st.checkbox(
                "Consider prerequisites", 
                value=True,
                help="Include prerequisite information in recommendations"
            )
            
            prefer_practical = st.checkbox(
                "Prefer practical/hands-on courses",
                value=False,
                help="Prioritize courses with practical components"
            )
        
        # Build enhanced query
        enhanced_query = query
        if difficulty_pref != "Any":
            enhanced_query += f" I prefer {difficulty_pref.lower()} courses."
        if category_pref != "Any":
            enhanced_query += f" I'm looking for {category_pref.lower()} courses."
        if prefer_practical:
            enhanced_query += " I prefer hands-on, practical courses with projects."
        
        return enhanced_query, num_recommendations if enhanced_query.strip() else (None, 5)
    
    def render_recommendations(self, response: ValidatedRecommendationResponse, show_debug: bool = False):
        """Render the course recommendations"""
        if not response.recommendations:
            st.warning("No recommendations found. Try refining your query.")
            return
        
        st.header(f"📚 Recommended Courses ({len(response.recommendations)} found)")
        
        # Overall confidence indicator
        confidence_color = self.get_confidence_color(response.overall_confidence)
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h3>Overall Confidence: <span class="{confidence_color}">{response.overall_confidence:.1%}</span></h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendations grid
        for i, rec in enumerate(response.recommendations):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Course card
                    st.markdown(f"""
                    <div class="course-card">
                        <h3>🎯 {rec.course_id}: {rec.title}</h3>
                        <p><strong>Match Score:</strong> <span class="{self.get_confidence_color(rec.match_score)}">{rec.match_score:.1%}</span></p>
                        <p><strong>Why this course:</strong> {rec.justification}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Course details from data
                    course_data = next((c for c in self.courses if c['code'] == rec.course_id), None)
                    if course_data:
                        with st.expander(f"📋 Course Details: {rec.course_id}"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write(f"**Credits:** {course_data.get('credits', 'N/A')}")
                                st.write(f"**Difficulty:** {course_data.get('difficulty', 'N/A')}/5")
                                st.write(f"**Category:** {course_data.get('category', 'N/A')}")
                            with col_b:
                                st.write(f"**Semester:** {course_data.get('semester', 'N/A')}")
                                st.write(f"**Prerequisites:** {course_data.get('prerequisites', 'N/A')}")
                                st.write(f"**Instructor:** {course_data.get('instructor', 'N/A')}")
                            
                            st.write(f"**Description:** {course_data.get('description', 'No description available')}")
                
                with col2:
                    # Feedback buttons
                    self.render_feedback_buttons(rec.course_id, i)
        
        # Warnings and debug info
        if response.warnings:
            with st.expander("⚠️ Validation Warnings"):
                for warning in response.warnings:
                    st.warning(warning)
        
        if show_debug:
            with st.expander("🔍 Debug Information"):
                st.json({
                    "validation_passed": response.validation_passed,
                    "fallback_triggered": response.fallback_triggered,
                    "processing_time": "N/A",  # Would need to track this
                    "query_embedding_used": "Yes"
                })
    
    def render_feedback_buttons(self, course_id: str, index: int):
        """Render feedback buttons for a course recommendation"""
        st.markdown(f"""
        <div class="feedback-section">
            <p style="font-size: 0.9rem; margin-bottom: 0.5rem;"><strong>Helpful?</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("👍", key=f"thumbs_up_{course_id}_{index}", help="This recommendation is helpful"):
                self.record_feedback(course_id, "positive", "Thumbs up")
                st.success("Thanks for your feedback!")
        
        with col_b:
            if st.button("👎", key=f"thumbs_down_{course_id}_{index}", help="This recommendation is not helpful"):
                self.record_feedback(course_id, "negative", "Thumbs down")
                st.info("Thanks! We'll improve our recommendations.")
    
    def render_refinement_section(self):
        """Render the query refinement section"""
        st.header("🔄 Refine Your Search")
        
        st.markdown("""
        <div class="refinement-tips">
            <h4>💡 Refinement Tips:</h4>
            <ul>
                <li>Be more specific about your interests</li>
                <li>Mention your current skill level</li>
                <li>Specify time preferences (online, evening, etc.)</li>
                <li>Include career goals or project interests</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        refinement_query = st.text_input(
            "Add more details or preferences:",
            placeholder="Example: I prefer online courses, I'm a beginner in programming, I want courses with practical projects...",
            key="refinement_input"
        )
        
        if refinement_query:
            return refinement_query
        return None
    
    def render_analytics_dashboard(self):
        """Render analytics dashboard for feedback and usage"""
        if not st.session_state.feedback_data and not st.session_state.query_history:
            return
        
        with st.expander("📊 Usage Analytics"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.feedback_data:
                    feedback_df = pd.DataFrame(st.session_state.feedback_data)
                    positive_count = len(feedback_df[feedback_df['sentiment'] == 'positive'])
                    negative_count = len(feedback_df[feedback_df['sentiment'] == 'negative'])
                    
                    fig = px.pie(
                        values=[positive_count, negative_count],
                        names=['Positive', 'Negative'],
                        title="Feedback Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if st.session_state.query_history:
                    query_counts = len(st.session_state.query_history)
                    st.metric("Total Queries", query_counts)
                    
                    if st.session_state.recommendations:
                        avg_confidence = st.session_state.recommendations.overall_confidence
                        st.metric("Last Confidence", f"{avg_confidence:.1%}")
    
    def get_confidence_color(self, confidence: float) -> str:
        """Get CSS class based on confidence level"""
        if confidence >= 0.7:
            return "confidence-high"
        elif confidence >= 0.4:
            return "confidence-medium"
        else:
            return "confidence-low"
    
    def record_feedback(self, course_id: str, sentiment: str, comment: str):
        """Record user feedback"""
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "course_id": course_id,
            "sentiment": sentiment,
            "comment": comment
        }
        st.session_state.feedback_data.append(feedback)
        logger.info(f"Recorded feedback: {feedback}")
    
    def save_feedback_to_file(self):
        """Save feedback data to file"""
        if st.session_state.feedback_data:
            feedback_file = Path("data/user_feedback.json")
            feedback_file.parent.mkdir(exist_ok=True)
            
            try:
                with open(feedback_file, "w") as f:
                    json.dump(st.session_state.feedback_data, f, indent=2)
                logger.info(f"Saved {len(st.session_state.feedback_data)} feedback entries")
            except Exception as e:
                logger.error(f"Error saving feedback: {e}")
    
    def run(self):
        """Main application runner"""
        # Load pipeline
        if not self.load_pipeline():
            st.stop()
        
        # Render UI components
        self.render_header()
        confidence_threshold, show_debug = self.render_sidebar()
        
        # Main content area
        query, num_recs = self.render_query_input()
        
        # Process query
        if query and st.button("🚀 Get Recommendations", type="primary"):
            with st.spinner("🤖 Generating personalized recommendations..."):
                try:
                    # Update pipeline confidence threshold
                    self.pipeline.confidence_threshold = confidence_threshold
                    
                    # Process query
                    response = self.pipeline.process_query_with_validation(query, top_k=num_recs)
                    st.session_state.recommendations = response
                    st.session_state.query_history.append(query)
                    
                    logger.info(f"Generated {len(response.recommendations)} recommendations for query: {query[:50]}...")
                    
                except Exception as e:
                    st.error(f"Error generating recommendations: {e}")
                    logger.error(f"Recommendation error: {e}")
        
        # Display recommendations
        if st.session_state.recommendations:
            self.render_recommendations(st.session_state.recommendations, show_debug)
            
            # Refinement section
            refinement = self.render_refinement_section()
            if refinement and st.button("🔄 Refine Search"):
                # Combine original query with refinement
                original_query = st.session_state.query_history[-1] if st.session_state.query_history else ""
                combined_query = f"{original_query} {refinement}"
                
                with st.spinner("🔄 Refining recommendations..."):
                    try:
                        response = self.pipeline.process_query_with_validation(combined_query, top_k=num_recs)
                        st.session_state.recommendations = response
                        st.session_state.refined_queries.append(refinement)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error refining recommendations: {e}")
        
        # Analytics dashboard
        self.render_analytics_dashboard()
        
        # Save feedback periodically
        if st.session_state.feedback_data:
            self.save_feedback_to_file()


def main():
    """Main entry point for the Streamlit application"""
    try:
        app = StreamlitCourseRecommender()
        app.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()
