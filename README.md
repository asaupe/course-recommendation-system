# 🎓 AI Course Recommendation System

> **GenAI-powered course discovery using RAG, embeddings, and intelligent guardrails**

A sophisticated course recommendation system that helps students find relevant courses based on their interests, goals, and academic requirements. Built with cutting-edge AI technologies including Retrieval-Augmented Generation (RAG), OpenAI embeddings, and intelligent validation systems.

## ✨ Features

🤖 **AI-Powered Recommendations** - Uses GPT and embeddings for intelligent course matching  
🔍 **Semantic Search** - Vector-based similarity search with FAISS indexing  
🛡️ **Smart Guardrails** - Validates responses and prevents hallucinations  
🎨 **Modern Web Interface** - Interactive Streamlit app with real-time recommendations  
🔄 **Query Refinement** - Iterative search improvement based on user feedback  
📊 **Analytics Dashboard** - Usage metrics and recommendation insights  

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- 4GB+ RAM (for embeddings)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd course-recommendation-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API key:
   # OPENAI_API_KEY=your_api_key_here
   ```

5. **Launch the application**
   ```bash
   # Easy launch with setup verification
   ./run_streamlit_app.sh
   
   # Or manual launch
   streamlit run day6_streamlit_app.py
   ```

6. **Open in browser**
   ```
   http://localhost:8501
   ```

## 📖 Usage Guide

### Basic Usage

1. **Enter your interests**: Describe what you want to learn
2. **Set preferences**: Choose difficulty level, category, format
3. **Get recommendations**: AI generates personalized course suggestions
4. **Refine search**: Add more details to improve results
5. **Provide feedback**: Rate recommendations to help improve the system

### Example Queries

```
"I want to learn machine learning and data analysis"
"I need beginner programming courses with hands-on projects"
"I'm interested in web development for my career change"
"I want advanced algorithms courses for graduate school prep"
```

### Query Tips

- **Be specific**: Include your background, goals, and preferences
- **Mention constraints**: Time availability, difficulty preferences, format needs
- **Use refinement**: Add more details if initial results aren't perfect
- **Provide feedback**: Help improve recommendations for future users

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │────│   Guardrails    │────│   RAG Pipeline │
│   (Frontend)    │    │  (Validation)   │    │   (Core AI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       │
                         ┌─────────────────┐    ┌─────────────────┐
                         │  Course Data    │────│  Vector Search  │
                         │    (JSON)       │    │   (FAISS)       │
                         └─────────────────┘    └─────────────────┘
```

### Key Components

- **Frontend**: Interactive Streamlit web application
- **Guardrails**: Pydantic validation and hallucination detection
- **RAG Pipeline**: Retrieval-augmented generation with context injection
- **Vector Search**: FAISS-based semantic similarity search
- **Data Layer**: Course information and embeddings storage

## 🧪 Testing

### Run All Tests
```bash
# Using the test runner
python tests/run_tests.py

# Specific test categories
python tests/run_tests.py --category

# Specific module
python tests/run_tests.py --module test_data_manager

# With verbose output
python tests/run_tests.py -vv
```

### Test Coverage
- Unit tests for all core modules
- Integration tests for end-to-end workflows
- Scenario tests for real-world use cases
- Performance benchmarks

### Day 7 Test Scenarios
```bash
# Run comprehensive test scenarios
python day7_test_scenarios.py

# Includes:
# - STEM major with humanities interest
# - Student missing graduation credits
# - Career changer requirements
# - High achiever advanced courses
# - Learning preference accommodation
```

## 📁 Project Structure

```
course-recommendation-system/
├── 📄 README.md                 # This file
├── 📄 DOCUMENTATION.md          # Detailed system documentation
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example             # Environment template
├── � Dockerfile              # Container configuration
├── 🗂️ data/                    # Course data and storage
│   ├── courses.json            # Course catalog
│   ├── user_feedback.json      # User feedback data
│   └── day7_test_results.json  # Test scenario results
├── 🗂️ src/                     # Core application modules
│   ├── data_manager.py         # Course data loading
│   ├── rag_system.py           # ChromaDB RAG implementation
│   └── course_recommender.py   # LLM integration
├── 🗂️ tests/                   # Test suite
│   ├── run_tests.py            # Test runner
│   ├── test_data_manager.py    # Data layer tests
│   ├── test_rag_system.py      # RAG system tests
│   ├── test_embedding_search.py # Vector search tests
│   ├── test_guardrails.py      # Validation tests
│   └── test_integration.py     # End-to-end tests
├── 📄 day2_rag_test.py         # Day 2: RAG implementation
├── 📄 day3_embedding_search.py # Day 3: Vector search
├── 📄 day4_rag_pipeline.py     # Day 4: Complete pipeline
├── 📄 day5_guardrails.py       # Day 5: Validation system
├── 📄 day6_streamlit_app.py    # Day 6: Web interface
├── 📄 day7_test_scenarios.py   # Day 7: Comprehensive tests
├── 📄 verify_day*.py           # Daily verification scripts
└── 🗂️ .github/                 # CI/CD configuration
    └── workflows/
        └── ci-cd.yml           # GitHub Actions
```

## 📊 Daily Implementation Progress

- **Day 1**: ✅ Project setup and course data creation
- **Day 2**: ✅ RAG system with ChromaDB implementation  
- **Day 3**: ✅ Embedding-based search with FAISS
- **Day 4**: ✅ Complete RAG pipeline with confidence scoring
- **Day 5**: ✅ Guardrails, validation, and output filtering
- **Day 6**: ✅ Streamlit frontend with interactive features
- **Day 7**: ✅ Comprehensive testing and documentation

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
ENVIRONMENT=development          # development|production|testing
LOG_LEVEL=INFO                  # DEBUG|INFO|WARNING|ERROR
CONFIDENCE_THRESHOLD=0.6        # 0.0-1.0
MAX_RECOMMENDATIONS=10          # Maximum courses to return
```

## 🐛 Troubleshooting

### Common Issues

#### "OpenAI API Key not found"
```bash
# Solution: Set environment variable
export OPENAI_API_KEY=your_key_here
# Or edit .env file
```

#### "ChromaDB connection failed"
```bash
# Solution: Check disk space and permissions
# ChromaDB creates local database files
```

#### "Streamlit app won't start"
```bash
# Solution: Check port availability
streamlit run day6_streamlit_app.py --server.port 8502
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e .`)
4. Run tests (`python tests/run_tests.py`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing GPT and embedding APIs
- **Streamlit** for the excellent web framework
- **ChromaDB** for vector database capabilities
- **FAISS** for efficient similarity search

---

**Built with ❤️ for education and learning**
