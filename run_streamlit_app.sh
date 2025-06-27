#!/bin/bash

# Day 6: Streamlit App Launcher Script
# This script sets up and launches the course recommendation Streamlit app

echo "🎓 Course Recommendation System - Day 6"
echo "======================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your OpenAI API key"
    echo "   Required: OPENAI_API_KEY=your_api_key_here"
    read -p "Press Enter after setting up your API key..."
fi

# Check for required dependencies
echo "📦 Checking dependencies..."
python -c "import streamlit, openai, chromadb, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Verify core components
echo "🔍 Verifying system components..."
python verify_day6.py
if [ $? -ne 0 ]; then
    echo "❌ System verification failed. Please check the logs above."
    exit 1
fi

echo "✅ System verification passed!"
echo ""
echo "🚀 Launching Streamlit Course Recommendation App..."
echo "   📱 The app will open in your default browser"
echo "   🔗 URL: http://localhost:8501"
echo "   ⏹️  Press Ctrl+C to stop the app"
echo ""

# Launch Streamlit app
streamlit run day6_streamlit_app.py --server.port 8501 --server.address localhost

echo ""
echo "👋 Thanks for using the Course Recommendation System!"
