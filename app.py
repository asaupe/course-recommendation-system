import streamlit as st
import os
from dotenv import load_dotenv
from src.course_recommender import CourseRecommender
from src.data_manager import DataManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Course Recommendation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🎓 AI-Powered Course Recommendation System")
    st.markdown("Get personalized course recommendations based on your graduation requirements and interests!")
    
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Please configure your OpenAI API key in the .env file")
        st.code("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize components
    try:
        data_manager = DataManager()
        course_recommender = CourseRecommender()
        
        # Sidebar for user inputs
        with st.sidebar:
            st.header("📝 Your Information")
            
            # Student information
            student_name = st.text_input("Name", placeholder="Enter your name")
            major = st.selectbox("Major", ["Computer Science", "Engineering", "Business", "Liberal Arts", "Science"])
            year = st.selectbox("Academic Year", ["Freshman", "Sophomore", "Junior", "Senior"])
            
            # Graduation requirements
            st.subheader("🎯 Graduation Requirements")
            remaining_credits = st.number_input("Remaining Credits", min_value=0, max_value=200, value=60)
            required_categories = st.multiselect(
                "Required Course Categories",
                ["Core Requirements", "Major Electives", "General Education", "Math/Science", "Humanities"]
            )
            
            # Interests and preferences
            st.subheader("💡 Interests & Preferences")
            interests = st.text_area(
                "Areas of Interest",
                placeholder="e.g., machine learning, web development, data analysis, creative writing..."
            )
            
            learning_style = st.selectbox(
                "Preferred Learning Style",
                ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"]
            )
            
            difficulty_preference = st.slider(
                "Preferred Course Difficulty",
                min_value=1, max_value=5, value=3,
                help="1 = Easy, 5 = Very Challenging"
            )
            
            # Generate recommendations button
            generate_recs = st.button("🚀 Get Recommendations", type="primary")
        
        # Main content area
        if generate_recs and interests and required_categories:
            with st.spinner("🤖 Analyzing your profile and generating recommendations..."):
                try:
                    # Prepare user profile
                    user_profile = {
                        "name": student_name,
                        "major": major,
                        "year": year,
                        "remaining_credits": remaining_credits,
                        "required_categories": required_categories,
                        "interests": interests,
                        "learning_style": learning_style,
                        "difficulty_preference": difficulty_preference
                    }
                    
                    # Get recommendations
                    recommendations = course_recommender.get_recommendations(user_profile)
                    
                    # Display results
                    st.header("📚 Your Personalized Course Recommendations")
                    
                    for i, course in enumerate(recommendations, 1):
                        with st.expander(f"{i}. {course['title']} ({course['code']})"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Description:** {course['description']}")
                                st.write(f"**Why recommended:** {course['reason']}")
                                if course.get('prerequisites'):
                                    st.write(f"**Prerequisites:** {course['prerequisites']}")
                                
                            with col2:
                                st.metric("Credits", course['credits'])
                                st.metric("Difficulty", f"{course['difficulty']}/5")
                                st.write(f"**Category:** {course['category']}")
                                st.write(f"**Semester:** {course['semester']}")
                    
                    # Additional insights
                    st.header("📊 Planning Insights")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_recommended_credits = sum(course['credits'] for course in recommendations)
                        st.metric("Recommended Credits", total_recommended_credits)
                    
                    with col2:
                        avg_difficulty = sum(course['difficulty'] for course in recommendations) / len(recommendations)
                        st.metric("Average Difficulty", f"{avg_difficulty:.1f}/5")
                    
                    with col3:
                        categories_covered = len(set(course['category'] for course in recommendations))
                        st.metric("Categories Covered", categories_covered)
                    
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
        
        elif generate_recs:
            st.warning("Please fill in your interests and select at least one required category.")
        
        else:
            # Welcome screen
            st.markdown("""
            ## How it works:
            
            1. **📝 Tell us about yourself** - Enter your academic information in the sidebar
            2. **🎯 Set your goals** - Specify graduation requirements and remaining credits
            3. **💡 Share your interests** - Help us understand what you're passionate about
            4. **🚀 Get recommendations** - Our AI will suggest the best courses for you
            
            ### Features:
            - **Smart Matching**: Uses AI to match courses with your interests and requirements
            - **RAG Technology**: Retrieves relevant course information from our database
            - **Personalized Explanations**: Get reasons why each course is recommended for you
            - **Graduation Planning**: Tracks your progress toward degree completion
            """)
    
    except Exception as e:
        st.error(f"Application initialization error: {str(e)}")
        st.info("Please ensure all dependencies are installed and environment variables are configured.")

if __name__ == "__main__":
    main()
