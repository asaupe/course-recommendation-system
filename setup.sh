#!/bin/bash

# Course Recommendation System Development Setup Script

echo "🎓 Setting up Course Recommendation System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data chroma_db

# Copy environment template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your OpenAI API key"
fi

# Initialize data files
echo "📊 Initializing data files..."
python3 -c "
from src.data_manager import DataManager
dm = DataManager()
print('Data files initialized successfully!')
"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: streamlit run app.py"
echo "3. Open http://localhost:8501 in your browser"
echo ""
echo "For development:"
echo "- Run tests: python -m pytest tests/"
echo "- Format code: black ."
echo "- Lint code: flake8 ."
