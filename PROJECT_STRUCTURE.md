# Course Recommendation System - Project Structure

```
course-recommendation-system/
├── README.md                    # Main project documentation
├── TECHNICAL_DOCS.md           # Technical architecture documentation
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup configuration
├── setup.sh                    # Development setup script
├── create_github_repo.py       # GitHub repository setup script
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose configuration
├── .env.example               # Environment variables template
├── .env.dev                   # Development environment variables
├── .gitignore                 # Git ignore rules
├── app.py                     # Main Streamlit application
│
├── .github/                   # GitHub-specific files
│   ├── copilot-instructions.md # Copilot customization
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions CI/CD pipeline
│
├── .vscode/                   # VS Code configuration
│   └── tasks.json             # VS Code tasks (auto-generated)
│
├── src/                       # Source code modules
│   ├── __init__.py           # Package initialization
│   ├── course_recommender.py # Main recommendation engine
│   ├── rag_system.py         # RAG implementation with ChromaDB
│   ├── prompt_templates.py   # AI prompt templates
│   └── data_manager.py       # Data persistence and management
│
├── data/                      # Data files
│   ├── courses.json          # Course catalog data
│   └── requirements.json     # Graduation requirements
│
├── tests/                     # Unit tests
│   └── test_recommender.py   # Test suite for all components
│
└── chroma_db/                 # ChromaDB vector database (auto-created)
    └── (vector database files)
```

## Key Features Implemented

### 🤖 AI/ML Components
- **RAG System**: ChromaDB vector database for semantic course search
- **Prompt Engineering**: Carefully crafted prompts for optimal AI responses
- **OpenAI Integration**: GPT-3.5-turbo for intelligent recommendations
- **Fallback Systems**: Multiple layers of error handling and alternatives

### 🌐 Web Application
- **Streamlit Interface**: Modern, interactive web UI
- **Real-time Processing**: Live recommendation generation
- **User Profiles**: Comprehensive student information collection
- **Results Visualization**: Detailed course recommendations with explanations

### 🛠 Development Tools
- **Docker Support**: Complete containerization for easy deployment
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **Testing**: Comprehensive unit test suite with pytest

### 📊 Data Management
- **JSON Storage**: Course and requirement data in structured format
- **Pandas Integration**: Data analysis and manipulation capabilities
- **CRUD Operations**: Full data management functionality
- **Sample Data**: Pre-loaded course information for testing

### 🔧 Configuration
- **Environment Variables**: Secure API key management
- **Multiple Environments**: Development, testing, and production configs
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error recovery and user feedback

## Quick Start Commands

```bash
# Clone and setup (after creating GitHub repo)
git clone https://github.com/yourusername/course-recommendation-system.git
cd course-recommendation-system

# Setup development environment
chmod +x setup.sh
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the application
streamlit run app.py

# Run tests
python -m pytest tests/

# Docker deployment
docker-compose up
```

## GitHub Repository Setup

```bash
# Initialize and setup GitHub repository
python create_github_repo.py

# Follow the printed instructions to push to GitHub
```

This project structure provides a complete, production-ready course recommendation system that demonstrates advanced GenAI techniques including RAG, prompt engineering, and AI-powered personalization.
