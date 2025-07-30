# HackRX Policy QA API

A streamlined FastAPI application that provides intelligent Q&A capabilities for insurance policy documents with explainable AI responses. Features a single powerful endpoint that handles everything.

## 🚀 Key Features

- **Single Endpoint Design**: Everything you need in one `/hackrx/run` endpoint
- **Multi-format Document Support**: PDF and DOCX files
- **Explainable AI Responses**: Detailed reasoning, confidence scores, and source tracking
- **Advanced Clause Retrieval**: Semantic matching with clause-level citations
- **Enhanced Security**: API key authentication and input validation
- **Production Ready**: Comprehensive error handling and logging

## Quick Start

### 1. Environment Setup

```bash
# Copy and configure environment
cp .env.template .env

# Edit .env with your credentials
GEMINI_API_KEY=your_gemini_api_key_here
API_KEY=your_secure_api_key
```

### 2. Installation & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`

### 3. Testing

```bash
# Run comprehensive test suite
python test.py

# Test Render deployment readiness
python test_render.py

# Test sample request format
python test_sample.py
```

## 📊 API Usage

### Main Endpoint: `/hackrx/run`

This single endpoint handles document processing and Q&A with explainable responses.

#### Request Format

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": [
      "What is the grace period for premium payment?",
      "What are the exclusions mentioned in the policy?"
    ]
  }'
```

#### Enhanced Response Structure

```json
{
  "answers": [
    {
      "answer": "The grace period for premium payment is 30 days from the due date...",
      "confidence_score": 0.92,
      "source_clauses": [
        {
          "text": "A grace period of thirty days is allowed for payment of premium...",
          "page_number": 5,
          "confidence_score": 0.87
        }
      ],
      "reasoning": "Answer derived from analysis of 5 document sections. Key factors considered: document context relevance (78%), source clause alignment, and semantic similarity."
    }
  ]
}
```

#### Multiple Documents Support

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "https://example.com/policy1.pdf",
      "https://example.com/terms.docx"
    ],
    "questions": ["What is the coverage amount?"]
  }'
```

### Health Check: `/`

Simple endpoint to verify API status:

```bash
curl "http://localhost:8000/"
```

## 🏗️ Architecture & Features

### Document Processing Pipeline
1. **Multi-format Document Loader**: Supports PDF and DOCX files
2. **Intelligent Text Chunking**: Optimized for legal/insurance documents (1500 chars, 300 overlap)
3. **Advanced Embeddings**: Google Gemini embeddings with FAISS vector search
4. **Metadata Enrichment**: Page numbers, sections, and source tracking

### AI & Explainability
- **Confidence Scoring**: AI confidence levels for each answer (0.0 to 1.0)
- **Source Attribution**: Exact clause citations with page references
- **Reasoning Chains**: Detailed explanation of answer derivation
- **Context Relevance**: Semantic similarity scoring between questions and content

### Performance & Security
- **Async Processing**: Non-blocking document processing
- **Error Recovery**: Comprehensive error handling and graceful degradation
- **Input Validation**: File size limits and format validation
- **Authentication**: Bearer token authentication for all requests

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY` (required) - Your Google Gemini API key
- `API_KEY` (optional) - Custom API authentication key (default: "hackrx-2024-default-key")
- `ENVIRONMENT` (optional) - Environment setting (production/development)

### Supported File Formats

| Format | Extension | Features |
|--------|-----------|----------|
| PDF | .pdf | Page-level tracking, automatic text extraction |
| Word Document | .docx | Paragraph-level processing, structure preservation |

### File Size Limits
- Maximum file size: 50MB per document
- Automatic validation and error handling for oversized files

## 🚀 Deployment

### Docker
```dockerfile
# Use the provided Dockerfile
docker build -t hackrx-api .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e API_KEY=your_api_key \
  hackrx-api
```

### Render (Recommended Cloud Platform)
```bash
# Quick deployment using Blueprint (render.yaml)
# 1. Fork this repository to your GitHub account
# 2. Connect to Render Dashboard
# 3. Create new Blueprint from your repository
# 4. Set environment variables (GEMINI_API_KEY, API_KEY)
# 5. Deploy automatically

# Your API will be available at: https://your-service-name.onrender.com
```

**📖 For detailed Render deployment instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)**  
**📋 Use the [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) to ensure you're ready**

### Testing Render Deployment
```bash
# Test if your app is ready for Render
python test_render.py
```

#### Manual Render Deployment
```bash
# Alternative: Manual deployment via Render Dashboard
# 1. Create new Web Service on Render
# 2. Connect GitHub repository
# 3. Configure build and start commands:
#    Build Command: pip install -r requirements.txt
#    Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
# 4. Set environment variables in Render Dashboard
# 5. Deploy
```

### Production Considerations
- Set strong API keys for authentication
- Configure HTTPS in production
- Monitor API usage and performance
- Set up log aggregation for debugging

## 📚 Advanced Usage Examples

### Insurance Policy Analysis
```python
import requests

response = requests.post("http://localhost:8000/hackrx/run", 
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "documents": "https://example.com/health-policy.pdf",
        "questions": [
            "What is the waiting period for pre-existing conditions?",
            "Does this policy cover maternity expenses?",
            "What is the claim settlement ratio?",
            "Are mental health treatments covered?",
            "What is the room rent limit?"
        ]
    }
)

result = response.json()
for i, answer in enumerate(result['answers']):
    print(f"Q{i+1}: {answer['answer']}")
    print(f"Confidence: {answer['confidence_score']:.2%}")
    print(f"Sources: {len(answer['source_clauses'])} clauses found")
    print("---")
```

### Legal Document Review
```python
# Process legal terms and conditions
response = requests.post("http://localhost:8000/hackrx/run",
    headers={"Authorization": "Bearer your-api-key"}, 
    json={
        "documents": [
            "https://example.com/terms.pdf",
            "https://example.com/privacy-policy.docx"
        ],
        "questions": [
            "What are the cancellation terms?",
            "How is personal data protected?",
            "What are the liability limitations?"
        ]
    }
)
```

## 🛠️ Development

### Running Tests
```bash
# Run the test suite
python test.py

# Test individual components
python -c "import requests; print(requests.get('http://localhost:8000/').json())"
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Error Handling
The API provides detailed error messages for common issues:
- Invalid document URLs
- Unsupported file formats
- File size limitations
- Authentication failures
- Processing errors

## 📝 Request/Response Examples

### Basic Request
```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": ["What is covered under this policy?"]
}
```

### Basic Response
```json
{
  "answers": [
    {
      "answer": "This policy covers hospitalization expenses, surgery costs, and pre and post-hospitalization expenses as detailed in the policy document.",
      "confidence_score": 0.85,
      "source_clauses": [
        {
          "text": "The policy covers hospitalization expenses including room charges, nursing expenses, surgeon's fees...",
          "page_number": 3,
          "confidence_score": 0.92
        }
      ],
      "reasoning": "Answer derived from analysis of 3 document sections focusing on coverage details and policy benefits."
    }
  ]
}
```

## 🤝 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the test examples in `test.py`
3. Ensure your API key and Gemini key are correctly configured
4. Check the application logs for detailed error information

---

**HackRX Policy QA API** - Simplified, powerful, and ready for production insurance policy analysis.
