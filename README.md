# TestBot — SHL Assessment Recommendation Chatbot

A complete AI-powered conversational assessment recommendation system designed to help recruiters and hiring managers discover suitable SHL assessments through natural conversation.

## Features

✅ **Intelligent Requirement Parsing** - Extracts hiring requirements from vague queries  
✅ **Semantic Search** - FAISS-based vector retrieval for assessment matching  
✅ **Multi-factor Ranking** - Combines semantic similarity, skill overlap, and role matching  
✅ **Assessment Comparison** - Compare features between assessments using catalog data  
✅ **Refinement Support** - Adapt recommendations as user requirements evolve  
✅ **Guardrails & Safety** - Rejects off-topic and prompt injection requests  
✅ **Ollama Integration** - Local LLM support for natural conversation (optional)  
✅ **Strict API Schema** - Returns validated JSON responses only

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, FastAPI |
| **AI/LLM** | Ollama, llama3 |
| **Retrieval** | FAISS, sentence-transformers |
| **Scraping** | BeautifulSoup, requests |
| **Storage** | JSON |
| **Deployment** | Localhost, uvicorn |

## Project Structure

```
testbot/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── routes/
│   │   └── chat.py             # /chat endpoint
│   ├── services/
│   │   ├── parser.py           # Extract requirements from conversation
│   │   ├── retrieval.py        # FAISS embeddings & search
│   │   ├── ranking.py          # Rank assessments by relevance
│   │   ├── recommender.py      # Create recommendation list
│   │   ├── comparison.py       # Compare assessments
│   │   ├── guardrails.py       # Safety & scope protection
│   │   └── llm_service.py      # Ollama + llama3 integration
│   ├── models/
│   │   └── schemas.py          # Pydantic models & API schemas
│   └── utils/
│       └── helpers.py          # Utility functions
├── scraper/
│   └── scrape.py               # Fetch SHL catalog
├── data/
│   ├── shl_catalog.json        # Raw catalog
│   └── processed_catalog.json  # Processed for embeddings
├── vectorstore/
│   ├── faiss.index             # Vector index
│   └── metadata.pkl            # Vector metadata
├── tests/
│   └── sample_conversations.json  # Test cases
├── requirements.txt
└── README.md
```

## Setup & Installation

### Prerequisites

- Python 3.9+
- Ollama (optional, for enhanced conversation)
- pip or conda

### Step 1: Create Virtual Environment

```bash
cd s:\chatbotagent\testbot
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Generate SHL Catalog

```bash
python scraper/scrape.py
# Creates: data/shl_catalog.json
```

### Step 4: Generate Embeddings & FAISS Index

```bash
python -c "from app.services.retrieval import CatalogProcessor; 
processor = CatalogProcessor(); 
processor.run_full_pipeline()"

# Creates:
# - data/processed_catalog.json
# - vectorstore/faiss.index
# - vectorstore/metadata.pkl
```

### Step 5: (Optional) Start Ollama

For enhanced conversational responses:

```bash
ollama serve
# In another terminal:
ollama pull llama3
```

### Step 6: Run TestBot Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at: `http://localhost:8000`

## API Usage

### Health Check

```bash
GET http://localhost:8000/health

Response:
{
  "status": "healthy",
  "service": "TestBot Chat",
  "vectorstore_ready": true,
  "ollama_available": true
}
```

### Chat Endpoint

```bash
POST http://localhost:8000/chat

Request:
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring mid-level Java developer with Spring Boot skills"
    }
  ]
}

Response:
{
  "reply": "Based on your requirements, I recommend...",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/...",
      "test_type": "K",
      "description": "Knowledge test for Java 8 programming",
      "skills": ["Java", "Java 8", "programming"]
    }
  ],
  "end_of_conversation": false
}
```

### Request Schema

```python
{
  "messages": [
    {
      "role": "user" | "assistant",
      "content": "string"
    }
  ]
}
```

### Response Schema

```python
{
  "reply": "string",
  "recommendations": [
    {
      "name": "string",
      "url": "string",
      "test_type": "P|K|A|S|O",
      "description": "string (optional)",
      "skills": ["string"] (optional)
    }
  ],
  "end_of_conversation": "boolean"
}
```

## Workflow

### 1. User Sends Request
```
POST /chat
{
  "messages": [{"role": "user", "content": "Hiring Java developer"}]
}
```

### 2. Safety Check (Guardrails)
- Checks for off-topic keywords
- Detects prompt injection attempts
- Validates on-topic scope

### 3. Request Parsing
- Extracts job role
- Identifies experience level
- Identifies skills and traits
- Detects personality requirements

### 4. Clarification Logic
- If role or experience missing → Ask clarification questions
- Returns list of 2-3 targeted questions

### 5. Semantic Search (FAISS)
- Converts request to embedding
- Searches vectorized catalog
- Returns top 15 candidates

### 6. Multi-factor Ranking
- Combines semantic similarity (50%)
- Skill overlap (30%)
- Role match (20%)
- Filters low-scoring results

### 7. Recommendation Creation
- Selects top 5 assessments
- Validates all have URLs (catalog-only)
- Formats with descriptions and skills

### 8. Response Generation
- Creates natural language reply
- Includes recommendations list
- Returns strict JSON schema

## API Rules & Constraints

✅ **Must Do**:
- Use SHL catalog only
- Ask clarification for vague requests
- Support assessment refinements
- Support assessment comparisons
- Return strict JSON schema
- Stay stateless

❌ **Must NOT**:
- Hallucinate assessments
- Recommend external tests
- Give general hiring advice
- Violate response schema
- Cache state between requests

## Assessment Types

| Code | Type | Example |
|------|------|---------|
| **P** | Personality | OPQ32r |
| **K** | Knowledge | Java 8, Spring Framework |
| **A** | Ability/Reasoning | Verify Verbal Reasoning, Critical Reasoning |
| **S** | Situational Judgment | Verify Situational Judgment |
| **O** | Other | Various |

## Examples

### Example 1: Vague Query → Clarification

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "I'm hiring"}
  ]
}
```

**Response**:
```json
{
  "reply": "To help you find the best assessment, what type of role are you hiring for? What experience level?",
  "recommendations": [],
  "end_of_conversation": false
}
```

### Example 2: Specific Requirements → Recommendations

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "Senior frontend developer with React expertise"}
  ]
}
```

**Response**:
```json
{
  "reply": "Based on your requirements, I recommend:\n\n1. React Knowledge (Knowledge)",
  "recommendations": [
    {
      "name": "React Knowledge",
      "url": "https://www.shl.com/en/products/individual-test-solutions/react/",
      "test_type": "K",
      "skills": ["React", "JavaScript", "frontend", "web development"]
    },
    {
      "name": "Verify Critical Reasoning",
      "url": "https://www.shl.com/en/products/individual-test-solutions/verify-critical-reasoning/",
      "test_type": "A",
      "skills": ["reasoning", "logical thinking", "problem solving"]
    }
  ],
  "end_of_conversation": false
}
```

### Example 3: Assessment Comparison

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "What's the difference between OPQ32r and Verify Situational Judgment?"}
  ]
}
```

**Response**:
```json
{
  "reply": "## Comparison: OPQ32r vs Verify Situational Judgment\n\n### Duration\n- OPQ32r: 25 minutes\n- Verify Situational Judgment: 20 minutes\n\n### Test Type\n- OPQ32r: Personality\n- Verify Situational Judgment: Situational Judgment\n\n...",
  "recommendations": [],
  "end_of_conversation": false
}
```

### Example 4: Off-topic Rejection

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "What's the average developer salary?"}
  ]
}
```

**Response**:
```json
{
  "reply": "I can't assist with salary. I'm specialized in SHL assessment recommendations. How can I help you find the right assessment for your hiring needs?",
  "recommendations": [],
  "end_of_conversation": false
}
```

## Testing

Run sample conversations:

```bash
python -c "
import json

with open('tests/sample_conversations.json') as f:
    tests = json.load(f)

for test in tests:
    print(f'Test: {test[\"name\"]}')
    print(f'  Input: {test[\"conversation\"][0][\"content\"]}')
    print()
"
```

For API testing, use curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hiring Java developer"}]}'
```

Or use Python:

```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "messages": [
        {"role": "user", "content": "Hiring mid-level Python developer"}
    ]
})

print(response.json())
```

## Important Implementation Notes

1. **No Hallucination**: Recommendations ONLY from SHL catalog (FAISS index)
2. **Stateless**: Each request is independent; no persistent state
3. **Schema Strict**: Always validate with Pydantic schemas
4. **Guardrails**: Always check safety first
5. **LLM Optional**: Works without Ollama (uses fallbacks)
6. **Catalog-only**: Every recommendation must have a URL

## Troubleshooting

### Vectorstore not found
```
ERROR: Vectorstore not found
SOLUTION: Run: python -c "from app.services.retrieval import CatalogProcessor; processor = CatalogProcessor(); processor.run_full_pipeline()"
```

### Ollama service unavailable
```
WARNING: Ollama service not available
SOLUTION: Optional. Start with: ollama serve
TestBot works without Ollama using fallback responses.
```

### CORS errors when calling from frontend
```
Already handled by CORSMiddleware in main.py
Allow-Origins: * (configurable in production)
```

### Port 8000 already in use
```
SOLUTION: Use different port:
python -m uvicorn app.main:app --port 8080
```

## Performance Considerations

- **Embedding Generation**: ~5-10 seconds for 15 assessments
- **FAISS Search**: <10ms per query
- **Ranking**: <50ms
- **Total Response Time**: 100-300ms (without LLM), 2-5s (with Ollama)

## Security Notes

- ✅ Prompt injection detection active
- ✅ Off-topic content rejection enabled
- ✅ Catalog-only validation enforced
- ✅ CORS enabled (configurable)
- ⚠️ No authentication implemented (add for production)
- ⚠️ No rate limiting (add for production)

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Request rate limiting
- [ ] Response caching
- [ ] Multi-language support
- [ ] Extended assessment metadata
- [ ] Advanced ranking algorithms
- [ ] Feedback loop for model improvement
- [ ] PostgreSQL for catalog persistence

## License

SHL Assessment Recommendation Assignment

## Support

For issues or questions:
1. Check troubleshooting section
2. Review sample conversations in `tests/`
3. Enable debug mode in FastAPI
4. Check vectorstore and catalog files exist

---

**Version**: 1.0.0  
**Last Updated**: May 2026
