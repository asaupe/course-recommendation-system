# Course Recommendation System

A GenAI-powered course recommendation system that helps students pick classes based on graduation requirements and personal interests using prompt engineering, RAG (Retrieval-Augmented Generation), and the ChatGPT API.

## Features

- **Intelligent Course Recommendations**: Uses AI to suggest courses based on graduation requirements and student interests
- **RAG Implementation**: Retrieves relevant course information from a knowledge base
- **Prompt Engineering**: Carefully crafted prompts for optimal AI responses
- **Interactive Web Interface**: Streamlit-based UI for easy interaction
- **Graduation Planning**: Tracks progress toward degree requirements

## Tech Stack

- **Python 3.13+**
- **OpenAI GPT API** for natural language processing
- **ChromaDB** for vector storage and retrieval
- **Streamlit** for web interface
- **Pandas** for data manipulation
- **Scikit-learn** for additional ML features

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
