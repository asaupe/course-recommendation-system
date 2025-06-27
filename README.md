# Course Recommendation System

A GenAI-powered course recommendation system that helps students pick classes based on graduation requirements and personal interests using prompt engineering, RAG (Retrieval-Augmented Generation), and the ChatGPT API.

## Project Objective

This project builds a GenAI-powered assistant to help students choose courses aligned with their graduation requirements and personal interests using LLM classification and RAG. The system combines semantic search with intelligent AI reasoning to provide personalized, contextual course recommendations that consider both academic requirements and student preferences.

## System Architecture Overview

- **Input**: Student query about courses, graduation requirements, and personal interests
- **Profile Processing**: Extract student major, year, remaining credits, and learning preferences  
- **Intent Classification**: Identify whether request is for core requirements, electives, or general guidance
- **RAG Retrieval**: Search vector database (ChromaDB) for relevant courses matching student profile
- **Context Augmentation**: Combine retrieved course data with student profile and graduation requirements
- **LLM Generation**: Use OpenAI GPT to generate personalized recommendations with explanations
- **Response Formatting**: Structure output as detailed course recommendations with reasoning
- **Output**: JSON-structured response with course details, difficulty ratings, and personalized explanations

## Tech Stack

- **Python 3.13+**: Core development language with modern features
- **OpenAI API**: GPT-3.5-turbo for intelligent course recommendations and natural language processing
- **ChromaDB**: Vector database for semantic course search and retrieval (alternative to FAISS)
- **Streamlit**: Interactive web UI for student input and recommendation display
- **Pandas**: Data manipulation and analysis for course catalogs
- **Python-dotenv**: Environment variable management for API keys
- **Docker**: Containerization for consistent deployment across environments
- **Prompt Engineering**: Custom-crafted prompts for optimal AI performance (no LangChain dependency)

## Features

- **Intelligent Course Recommendations**: Uses AI to suggest courses based on graduation requirements and student interests
- **RAG Implementation**: Retrieves relevant course information from a knowledge base
- **Prompt Engineering**: Carefully crafted prompts for optimal AI responses
- **Interactive Web Interface**: Streamlit-based UI for easy interaction
- **Graduation Planning**: Tracks progress toward degree requirements

## Tech Stack

- **Python 3.13+**: Core development language with modern features and type hints
- **OpenAI GPT API**: GPT-3.5-turbo for natural language processing and intelligent recommendations
- **ChromaDB**: Vector database for semantic search and course retrieval (replaces FAISS)
- **Streamlit**: Interactive web interface for user input and recommendation display
- **Pandas**: Data manipulation and analysis for course catalog management
- **Scikit-learn**: Additional ML features for recommendation scoring and analysis
- **Docker**: Containerization for consistent deployment and development environments
- **Prompt Engineering**: Custom-designed prompts for optimal AI performance (no LangChain dependency)

## System Workflow

### 🔄 **How It Works**

1. **📝 Student Input Collection** - Gather academic profile via Streamlit interface:
   - Major, academic year, remaining credits
   - Required course categories for graduation
   - Personal interests and learning preferences
   - Difficulty preference and scheduling constraints

2. **🎯 Intent & Profile Processing** - Analyze student requirements:
   - Parse graduation requirements by major
   - Identify priority course categories (core, electives, general education)
   - Extract keywords from interest descriptions

3. **🔍 RAG Retrieval Phase** - Semantic course search:
   - Query ChromaDB vector database with student interests
   - Filter courses by required categories and prerequisites
   - Retrieve top candidate courses with similarity scores

4. **🤖 LLM Generation Phase** - AI-powered recommendation:
   - Combine student profile with retrieved course context
   - Generate personalized prompt with graduation requirements
   - Use OpenAI GPT to create detailed recommendations with explanations

5. **📊 Response Formatting & Display** - Structure and present results:
   - Parse AI response into structured course recommendations
   - Display courses with difficulty ratings, credit hours, and scheduling
   - Provide personalized explanations for each recommendation

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd AIGen2_coding_exercise
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Input your graduation requirements and interests to get personalized course recommendations

## Project Structure

```
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── course_recommender.py  # Core recommendation logic
│   ├── rag_system.py         # RAG implementation
│   ├── prompt_templates.py   # AI prompt templates
│   └── data_manager.py       # Course data management
├── data/
│   ├── courses.json          # Course catalog data
│   └── requirements.json     # Graduation requirements
├── tests/
│   └── test_recommender.py   # Unit tests
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
