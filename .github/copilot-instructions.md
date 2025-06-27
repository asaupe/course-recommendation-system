<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Course Recommendation System - Copilot Instructions

This is a Python project that implements a GenAI-powered course recommendation system using:
- OpenAI GPT API for natural language processing
- RAG (Retrieval-Augmented Generation) with ChromaDB for vector storage
- Streamlit for the web interface
- Prompt engineering techniques for optimal AI responses

## Code Guidelines

1. **Follow Python best practices**: Use type hints, docstrings, and PEP 8 styling
2. **Error handling**: Always include proper exception handling for API calls and data operations
3. **Async/await**: Use async programming for API calls where appropriate
4. **Testing**: Write unit tests for all core functions
5. **Environment variables**: Use python-dotenv for configuration management
6. **Logging**: Implement proper logging for debugging and monitoring

## Project-Specific Patterns

- Use Pydantic models for data validation where appropriate
- Implement caching for expensive operations (embeddings, API calls)
- Follow the RAG pattern: retrieve relevant context, augment prompts, generate responses
- Use prompt templates for consistent AI interactions
- Implement proper error boundaries in Streamlit components

## Key Libraries and Their Usage

- **OpenAI**: For GPT API interactions and embeddings
- **ChromaDB**: For vector storage and similarity search
- **Streamlit**: For web UI components and state management
- **Pandas**: For course data manipulation and analysis
- **Scikit-learn**: For additional ML features if needed
