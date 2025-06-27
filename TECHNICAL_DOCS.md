# Course Recommendation System - Technical Documentation

## Architecture Overview

The Course Recommendation System is built using a modular architecture that combines several advanced AI techniques:

### Core Components

1. **RAG System (`src/rag_system.py`)**
   - Uses ChromaDB for vector storage and similarity search
   - Embeds course information for semantic retrieval
   - Fallback to text-based search when vector DB is unavailable

2. **Course Recommender (`src/course_recommender.py`)**
   - Main orchestrator that combines RAG retrieval with AI generation
   - Uses OpenAI GPT API for intelligent course recommendations
   - Implements both AI-powered and rule-based recommendation fallbacks

3. **Prompt Templates (`src/prompt_templates.py`)**
   - Carefully crafted prompts for optimal AI responses
   - Templates for different use cases (recommendations, analysis, planning)
   - Incorporates prompt engineering best practices

4. **Data Manager (`src/data_manager.py`)**
   - Handles course and requirement data persistence
   - Provides CRUD operations for course information
   - Supports JSON-based data storage with pandas integration

5. **Streamlit App (`app.py`)**
   - User-friendly web interface
   - Real-time recommendation generation
   - Interactive forms and result visualization

## AI/ML Techniques Used

### 1. Retrieval-Augmented Generation (RAG)
```python
# RAG Pipeline
user_query → vector_search(courses) → relevant_context → LLM_generation → recommendations
```

- **Retrieval**: ChromaDB performs similarity search on course embeddings
- **Augmentation**: Retrieved courses are added to the AI prompt as context
- **Generation**: GPT generates personalized recommendations with explanations

### 2. Prompt Engineering
The system uses several prompt engineering techniques:

- **System Prompts**: Establish AI role and behavior guidelines
- **Few-shot Learning**: Examples in prompts to guide response format
- **Chain of Thought**: Structured reasoning in recommendation explanations
- **Context Injection**: Dynamic course data insertion into prompts

### 3. Fallback Strategies
- Vector search → Text search → Sample data
- AI recommendations → Rule-based → Default courses
- Multiple error handling layers ensure system reliability

## Data Flow

```
User Input → Profile Processing → RAG Search → AI Generation → Response Formatting → UI Display
```

1. **User Profile**: Collected via Streamlit interface
2. **Interest Matching**: RAG system finds relevant courses
3. **AI Processing**: GPT analyzes profile and generates recommendations
4. **Response Parsing**: Structured data extraction from AI response
5. **UI Rendering**: Streamlit displays recommendations with explanations

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
DEBUG=True
LOG_LEVEL=INFO
```

### Data Files
- `data/courses.json`: Course catalog information
- `data/requirements.json`: Graduation requirements by major
- `chroma_db/`: Vector database persistence directory

## API Integration

### OpenAI GPT API
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=2000
)
```

- **Model**: GPT-3.5-turbo for cost-effectiveness
- **Temperature**: 0.7 for balanced creativity and consistency
- **Token Limit**: 2000 for detailed recommendations

### ChromaDB Vector Store
```python
collection.add(
    documents=course_descriptions,
    metadatas=course_metadata,
    ids=course_codes
)

results = collection.query(
    query_texts=[user_interests],
    n_results=max_courses
)
```

## Error Handling

The system implements multiple layers of error handling:

1. **API Failures**: Fallback to rule-based recommendations
2. **Data Issues**: Default to sample data
3. **Vector DB Problems**: Text-based search fallback
4. **Invalid Input**: User-friendly error messages

## Performance Optimizations

1. **Caching**: Vector embeddings and API responses
2. **Lazy Loading**: Components initialized only when needed
3. **Batch Processing**: Multiple courses processed together
4. **Connection Pooling**: Efficient API usage

## Testing Strategy

### Unit Tests (`tests/test_recommender.py`)
- Component isolation with mocking
- Edge case coverage
- Data validation tests
- API integration tests

### Integration Tests
- End-to-end workflow testing
- UI component testing
- Data persistence validation

## Deployment Options

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker Deployment
```bash
docker-compose up
```

### Cloud Deployment
- Supports deployment to AWS, GCP, Azure
- Environment-specific configurations
- Scalable architecture design

## Security Considerations

1. **API Key Management**: Environment variables only
2. **Input Validation**: Sanitized user inputs
3. **Data Privacy**: No PII storage
4. **Rate Limiting**: API usage controls

## Future Enhancements

1. **Advanced ML Models**: Fine-tuned models for specific domains
2. **Real-time Learning**: User feedback integration
3. **Multi-modal RAG**: Support for images, videos in course data
4. **Advanced Analytics**: Learning outcome predictions
5. **Mobile App**: React Native or Flutter implementation
