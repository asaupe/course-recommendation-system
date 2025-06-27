# Course Recommendation System - Documentation

## 📖 Overview

This Course Recommendation System is a GenAI-powered application that helps students discover relevant courses based on their interests, goals, and academic requirements. The system uses advanced AI techniques including Retrieval-Augmented Generation (RAG), embeddings-based search, and natural language processing to provide personalized course recommendations.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Streamlit UI   │  │   CLI Interface │                   │
│  │   (Day 6)       │  │   (Optional)    │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         Day 5: Guardrails & Validation                 │ │
│  │  • Pydantic Models      • Output Validation           │ │
│  │  • Course ID Filtering  • Confidence Scoring          │ │
│  │  • Hallucination Detection • Fallback Mechanisms     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Day 4: RAG Pipeline                          │ │
│  │  • Query Processing     • Context Injection            │ │
│  │  • Document Retrieval   • LLM Response Generation     │ │
│  │  • Confidence Scoring   • Structured Output           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │        Day 3: Embedding Search                         │ │
│  │  • OpenAI Embeddings    • FAISS Vector Index          │ │
│  │  • Similarity Search    • Course Ranking              │ │
│  │  • Query Embedding      • Result Filtering            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Course Data    │  │   ChromaDB      │                   │
│  │   (JSON)        │  │  (Vector Store) │                   │
│  │   Day 1-2       │  │    Day 2        │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 External Services                           │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   OpenAI API    │  │   Other APIs    │                   │
│  │  • GPT Models   │  │   (Future)      │                   │
│  │  • Embeddings   │  │                 │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input Processing**: User query received through Streamlit interface
2. **Query Enhancement**: Query processed and enhanced with user preferences
3. **Embedding Generation**: Query converted to vector representation using OpenAI embeddings
4. **Similarity Search**: FAISS index searched for similar courses
5. **Context Retrieval**: Relevant course information retrieved and formatted
6. **RAG Processing**: Context injected into prompt for LLM
7. **Response Generation**: GPT model generates structured recommendations
8. **Validation & Guardrails**: Output validated against known courses and quality standards
9. **Result Presentation**: Recommendations displayed with explanations and confidence scores

## 🔧 Technical Stack

### Core Technologies
- **Python 3.9+**: Primary programming language
- **OpenAI API**: GPT models and text embeddings
- **Streamlit**: Web interface framework
- **FAISS**: Vector similarity search
- **ChromaDB**: Vector database for RAG
- **Pydantic**: Data validation and parsing

### Dependencies
```python
openai>=1.0.0          # AI model integration
streamlit>=1.28.0      # Web interface
chromadb>=0.4.0        # Vector database
faiss-cpu>=1.7.0       # Similarity search
pydantic>=2.0.0        # Data validation
pandas>=2.0.0          # Data manipulation
numpy>=1.24.0          # Numerical operations
plotly>=5.15.0         # Interactive visualizations
python-dotenv>=1.0.0   # Environment management
scikit-learn>=1.3.0    # Additional ML utilities
```

## 🤖 AI Integration & Usage

### OpenAI API Usage

#### Text Embeddings (text-embedding-3-small)
- **Purpose**: Convert course descriptions and user queries to vector representations
- **Usage Pattern**: Batch processing for course data, real-time for user queries
- **Cost Optimization**: Caching of course embeddings, efficient batching
- **Rate Limiting**: Implemented with exponential backoff

#### GPT-3.5-Turbo for Response Generation
- **Purpose**: Generate natural language explanations and recommendations
- **Prompt Engineering**: Structured prompts with context injection
- **Temperature**: 0.3 (lower for consistency in structured output)
- **Token Management**: Limited to 1500 tokens for responses

### Prompt Engineering Strategy

#### System Prompt
```
You are a course advisor. Always respond with valid JSON containing course 
recommendations with required fields: course_id, title, justification, and match_score.
```

#### Context Injection
```
Based on the student query: "{query}"

Relevant courses from our database:
{context}

Provide recommendations as JSON with the following structure:
{
  "recommendations": [...],
  "overall_confidence": 0.0-1.0,
  "reasoning": "explanation"
}
```

### RAG Implementation

1. **Retrieval Phase**:
   - Query embedding generation
   - Vector similarity search (cosine similarity)
   - Top-K course retrieval (default: 5)

2. **Augmentation Phase**:
   - Context formatting and injection
   - Prompt template population
   - Metadata inclusion

3. **Generation Phase**:
   - LLM query with structured prompt
   - JSON response parsing
   - Validation and post-processing

## 📊 Data Management

### Course Data Structure
```json
{
  "code": "CS101",
  "title": "Introduction to Computer Science",
  "description": "Comprehensive course description...",
  "credits": 3,
  "difficulty": 2,
  "category": "Core Requirements",
  "semester": "Fall/Spring",
  "prerequisites": "None",
  "instructor": "Dr. Smith",
  "schedule": "MWF 10:00-11:00 AM"
}
```

### Data Sources
- **Primary**: JSON file with curated course information
- **Future**: Integration with university course catalogs
- **Validation**: Automated consistency checks and manual review

### Vector Storage
- **ChromaDB**: Persistent vector storage for RAG
- **FAISS**: In-memory index for fast similarity search
- **Embeddings**: 1536-dimensional vectors from OpenAI

## 🛡️ Quality Assurance & Guardrails

### Validation Layers

1. **Input Validation**:
   - Query length limits
   - Content filtering
   - User preference validation

2. **Course ID Validation**:
   - Whitelist-based filtering
   - Hallucination detection
   - Reference verification

3. **Output Validation**:
   - Pydantic model enforcement
   - Confidence score validation
   - Response structure verification

4. **Fallback Mechanisms**:
   - Low confidence detection
   - Generic response generation
   - Error recovery procedures

### Confidence Scoring

- **Match Score**: 0.0-1.0 per recommendation
- **Overall Confidence**: Aggregate system confidence
- **Threshold**: 0.6 default (configurable)
- **Fallback**: Triggered below threshold

## 🔍 Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/`):
   - Data manager functionality
   - RAG system components
   - Embedding search operations
   - Validation and guardrails

2. **Integration Tests**:
   - End-to-end pipeline testing
   - Multi-component interaction
   - Performance benchmarking
   - Error recovery testing

3. **Scenario Tests** (Day 7):
   - STEM major with humanities interest
   - Student missing graduation credits
   - Career changer requirements
   - High achiever advanced courses
   - Learning preference accommodation

### Test Coverage
- **Data Layer**: 95%+ coverage of core functionality
- **Application Layer**: 90%+ coverage of business logic
- **Integration**: Key user journeys and edge cases
- **Performance**: Response time and throughput benchmarks

## 🚀 Deployment & Operations

### Environment Configuration
```bash
OPENAI_API_KEY=your_api_key_here
ENVIRONMENT=production|development|testing
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
CONFIDENCE_THRESHOLD=0.6
```

### Deployment Options

1. **Local Development**:
   ```bash
   ./run_streamlit_app.sh
   # or
   streamlit run day6_streamlit_app.py
   ```

2. **Docker Container**:
   ```bash
   docker build -t course-recommender .
   docker run -p 8501:8501 course-recommender
   ```

3. **Cloud Deployment**:
   - Streamlit Cloud
   - Heroku
   - AWS/GCP/Azure

### Monitoring & Logging
- **Application Logs**: Structured logging with timestamps
- **Error Tracking**: Exception handling and reporting
- **Performance Metrics**: Response times and API usage
- **User Analytics**: Query patterns and feedback

## 📚 Assumptions & Limitations

### System Assumptions

1. **Data Quality**:
   - Course data is accurate and up-to-date
   - Prerequisites are correctly specified
   - Course descriptions are comprehensive

2. **User Behavior**:
   - Users provide meaningful query descriptions
   - Feedback is honest and constructive
   - Query intent is course discovery/recommendation

3. **Technical Environment**:
   - Stable internet connection for API calls
   - OpenAI API availability and rate limits
   - Sufficient computational resources

4. **Domain Scope**:
   - Focus on computer science courses
   - English language queries and content
   - Academic semester system

### Current Limitations

#### Data Limitations
- **Course Catalog Size**: Limited to ~10 sample courses
- **Real-time Updates**: No automatic course catalog synchronization
- **Multi-university**: Single institution focus
- **Historical Data**: No enrollment history or success rates

#### AI Model Limitations
- **Hallucination Risk**: LLM may generate non-existent courses
- **Context Window**: Limited by token constraints
- **Bias**: Potential biases in training data
- **Consistency**: Responses may vary for similar queries

#### Technical Limitations
- **Scalability**: Current architecture suitable for moderate usage
- **Offline Mode**: Requires internet connectivity
- **Personalization**: Limited user profile persistence
- **Multi-language**: English-only support

#### Functional Limitations
- **Prerequisites**: Basic prerequisite checking only
- **Scheduling**: No real-time schedule conflict detection
- **Capacity**: No enrollment capacity considerations
- **Cost**: No tuition or fee calculations

### Known Issues & Mitigation

1. **API Rate Limits**:
   - **Issue**: OpenAI API rate limiting
   - **Mitigation**: Exponential backoff, request batching

2. **Embedding Costs**:
   - **Issue**: High cost for large course catalogs
   - **Mitigation**: Caching, incremental updates

3. **Response Consistency**:
   - **Issue**: Varying recommendations for similar queries
   - **Mitigation**: Lower temperature, prompt engineering

4. **Error Recovery**:
   - **Issue**: API failures causing system errors
   - **Mitigation**: Graceful fallbacks, retry mechanisms

## 🔮 Future Enhancements

### Planned Improvements

1. **Enhanced Data Integration**:
   - Real university course catalog APIs
   - Student information systems integration
   - Live enrollment and capacity data
   - Professor ratings and reviews

2. **Advanced Personalization**:
   - User profile persistence
   - Learning style adaptation
   - Historical preference tracking
   - Collaborative filtering

3. **Expanded AI Capabilities**:
   - Multi-modal content (course videos, syllabi)
   - Advanced reasoning for complex requirements
   - Predictive success modeling
   - Natural language schedule planning

4. **Platform Enhancements**:
   - Mobile application
   - Integration with learning management systems
   - Advanced analytics dashboard
   - Bulk recommendation processing

5. **Quality Improvements**:
   - A/B testing framework
   - Recommendation explanation generation
   - Bias detection and mitigation
   - Continuous learning from feedback

### Research Opportunities

1. **Educational Data Mining**:
   - Course success prediction
   - Learning path optimization
   - Skill gap analysis

2. **Natural Language Processing**:
   - Query intent classification
   - Academic language understanding
   - Multi-language support

3. **Recommendation Systems**:
   - Hybrid recommendation approaches
   - Cold start problem solutions
   - Temporal dynamics modeling

## 📞 Support & Maintenance

### Development Team Contacts
- **Technical Lead**: Course Recommendation System Team
- **AI/ML Specialist**: RAG and embeddings expert
- **Frontend Developer**: Streamlit interface maintainer
- **Data Engineer**: Course data management

### Maintenance Schedule
- **Daily**: System health monitoring
- **Weekly**: Performance metrics review
- **Monthly**: Data quality assessment
- **Quarterly**: Model performance evaluation
- **Annually**: Major feature releases

### Issue Reporting
1. **Bug Reports**: Include steps to reproduce and system information
2. **Feature Requests**: Provide use case and business justification
3. **Data Issues**: Report inaccurate or missing course information
4. **Performance Issues**: Include query details and response times

---

**Document Version**: 1.0  
**Last Updated**: Day 7 Implementation  
**Next Review**: After production deployment
