# TestBot Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9+
- Git/Command line access

### Step 1: Installation (2 minutes)

```bash
cd s:\chatbotagent\testbot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize Data (1 minute)

```bash
# Generate SHL catalog and embeddings
python setup.py
```

This will:
- ✅ Scrape SHL catalog
- ✅ Generate embeddings
- ✅ Create FAISS index
- ✅ Verify everything works

### Step 3: Start Server (1 minute)

```bash
python -m uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

### Step 4: Test It (1 minute)

In another terminal:

```bash
python test.py
```

Or use curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hiring Java developer"}]}'
```

---

## 📝 Common Requests

### Ask for Recommendations
```json
{
  "messages": [
    {"role": "user", "content": "Hiring mid-level Java developer"}
  ]
}
```

### Get Clarification
```json
{
  "messages": [
    {"role": "user", "content": "I'm hiring"}
  ]
}
```

### Compare Assessments
```json
{
  "messages": [
    {"role": "user", "content": "Difference between OPQ32r and Verify Situational Judgment"}
  ]
}
```

---

## 🎯 Available Assessment Types

| Code | Type | Examples |
|------|------|----------|
| P | Personality | OPQ32r |
| K | Knowledge | Java 8, Python, Spring |
| A | Ability | Verify Reasoning tests |
| S | Situational | Verify Situational Judgment |

---

## 🔧 Optional: Enable Ollama

For enhanced conversational features:

```bash
# In one terminal:
ollama serve

# In another (one time):
ollama pull llama3

# Then start TestBot (will auto-detect Ollama)
python -m uvicorn app.main:app --reload
```

TestBot works fine without Ollama using fallback responses.

---

## 📊 API Documentation

Auto-generated docs at: **http://localhost:8000/docs**

Shows:
- All endpoints
- Request/response schemas
- Try-it-out interface

---

## ❓ FAQ

**Q: What if Ollama is not available?**
A: TestBot still works! Some responses use fallback templates instead of LLM-generated ones.

**Q: Can I use a different port?**
A: Yes! `python -m uvicorn app.main:app --port 8080 --reload`

**Q: How do I update the catalog?**
A: Run `python setup.py` again to rescrape and regenerate embeddings.

**Q: Can I deploy this to production?**
A: Yes, see README.md for security considerations and setup.

---

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Run sample tests** with `python test.py`
3. **Try interactive mode** with `python test.py interactive`
4. **Customize settings** in `config.py` (see below)
5. **Review API responses** in your browser at `/docs`

---

## ⚙️ Configuration

Create `config.py` in testbot/ directory to customize:

```python
# config.py
FAISS_INDEX_PATH = "vectorstore/faiss.index"
METADATA_PATH = "vectorstore/metadata.pkl"
CATALOG_PATH = "data/processed_catalog.json"

LLM_MODEL = "llama3"
LLM_BASE_URL = "http://localhost:11434"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MAX_RECOMMENDATIONS = 5
MIN_SCORE_THRESHOLD = 0.2

RANKING_WEIGHTS = {
    "semantic_similarity": 0.5,
    "skill_overlap": 0.3,
    "role_match": 0.2
}
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
python -m uvicorn app.main:app --port 8080 --reload
```

### Module not found
```bash
pip install -r requirements.txt
```

### Vectorstore missing
```bash
python setup.py
```

### Slow responses
- Ollama might be processing
- FAISS searches should be <10ms
- Embeddings are cached

---

**Version**: 1.0  
**Ready to test?** Run `python test.py`
