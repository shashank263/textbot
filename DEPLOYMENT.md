# TestBot - Production Deployment Guide

## Overview

This guide covers deploying TestBot to production on Windows, Linux, or cloud platforms.

## Prerequisites

- Python 3.9+
- Virtual environment support
- Ollama (optional, for LLM features)
- Docker (optional, for containerization)

## Deployment Options

### Option 1: Standalone Server (Recommended for Small Teams)

#### Step 1: Setup on Production Server

```bash
# SSH into server or use remote desktop

# Clone/copy TestBot
cd /opt/testbot  # or appropriate directory

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Generate Vectorstore

```bash
python setup.py
```

#### Step 3: Configure for Production

Edit `config.py`:

```python
DEBUG = False
API_HOST = "0.0.0.0"  # Listen on all interfaces
API_PORT = 8000
LOG_LEVEL = "WARNING"

# Optional: Add authentication
ENABLE_RATE_LIMIT = True
RATE_LIMIT_REQUESTS = 1000
RATE_LIMIT_WINDOW = 3600  # per hour
```

#### Step 4: Run with Production Server

```bash
# Using Gunicorn (Linux/Mac):
pip install gunicorn
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000

# Or use Uvicorn with more workers:
pip install uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Step 5: Setup Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/testbot

server {
    listen 80;
    server_name testbot.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo a2ensite testbot
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY testbot/ .

# Expose port
EXPOSE 8000

# Run setup (generates vectorstore)
RUN python setup.py

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2: Build Image

```bash
docker build -t testbot:1.0 .
```

#### Step 3: Run Container

```bash
docker run -d \
  --name testbot \
  -p 8000:8000 \
  -v testbot_data:/app/data \
  -v testbot_vectorstore:/app/vectorstore \
  testbot:1.0
```

#### Step 4: Setup Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  testbot:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./vectorstore:/app/vectorstore
    environment:
      - LOG_LEVEL=WARNING
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

Run with:
```bash
docker-compose up -d
```

### Option 3: Cloud Deployment

#### AWS (EC2 + RDS for vectorstore)

1. Launch EC2 instance (t3.medium or larger)
2. Security group: Allow port 8000, 22
3. Install Python 3.11
4. Follow "Standalone Server" setup
5. Use RDS for persistent catalog storage (optional)

#### Google Cloud (Cloud Run)

```bash
# Prepare Dockerfile (see Option 2)

# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/testbot

# Deploy
gcloud run deploy testbot \
  --image gcr.io/PROJECT_ID/testbot \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 600
```

#### Azure (App Service)

```bash
# Create resource group
az group create --name testbot-rg --location eastus

# Create app service plan
az appservice plan create \
  --name testbot-plan \
  --resource-group testbot-rg \
  --sku B2 --is-linux

# Deploy from Docker image
az webapp create \
  --resource-group testbot-rg \
  --plan testbot-plan \
  --name testbot \
  --deployment-container-image-name gcr.io/PROJECT_ID/testbot
```

## Security Configuration

### 1. Enable HTTPS

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ssl

# Create SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.load_cert_chain("path/to/cert.pem", "path/to/key.pem")
```

Or use nginx with Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d testbot.yourdomain.com
```

### 2. Add Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthCredential
from fastapi import Depends

security = HTTPBearer()

@app.post("/chat")
async def chat(request: ChatRequest, credentials: HTTPAuthCredential = Depends(security)):
    # Verify token
    if credentials.credentials != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=403)
    # ... rest of endpoint
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("100/minute")
async def chat(request: ChatRequest):
    # ...
```

### 4. Monitoring & Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('testbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## Performance Tuning

### 1. Database Optimization

Cache vectorstore in memory:

```python
# Load once on startup
import pickle

@app.on_event("startup")
async def load_vectorstore():
    global faiss_index, metadata
    with open("vectorstore/metadata.pkl", 'rb') as f:
        metadata = pickle.load(f)
    faiss_index = faiss.read_index("vectorstore/faiss.index")
```

### 2. Worker Configuration

```bash
# Gunicorn with worker pool
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --worker-connections 100 \
  --keepalive 5
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str):
    return _search_assessments(query)
```

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
curl http://localhost:8000/health

# Check vectorstore
curl http://localhost:8000/health | grep vectorstore_ready
```

### Metrics

Add Prometheus metrics:

```bash
pip install prometheus-client

from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
response_time = Histogram('chat_response_seconds', 'Response time')
```

## Maintenance

### Updating Catalog

```bash
# Run on-server
ssh user@server

# Pull latest catalog
python scraper/scrape.py

# Regenerate embeddings
python -c "from app.services.retrieval import CatalogProcessor; CatalogProcessor().run_full_pipeline()"

# No server restart needed (vectorstore loads on startup)
```

### Backup Strategy

```bash
# Backup vectorstore and data
tar -czf testbot_backup_$(date +%Y%m%d).tar.gz \
  data/ vectorstore/

# Upload to S3
aws s3 cp testbot_backup_*.tar.gz s3://my-backups/
```

### Log Rotation

```
# /etc/logrotate.d/testbot

/var/log/testbot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
}
```

## Troubleshooting

### Out of Memory

```bash
# Increase available memory
# Docker: add -m 4g flag
# VM: increase allocated RAM
# Reduce worker count in gunicorn
```

### Slow Responses

```bash
# Check FAISS search performance
time python -c "from app.services.retrieval import _search_assessments; _search_assessments('python developer')"

# Add caching if needed
# Increase workers
```

### Connection Issues

```bash
# Check if port is open
nc -zv localhost 8000

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp
```

## Scaling

For high traffic:

1. **Horizontal Scaling**: Run multiple instances behind load balancer
2. **Shared Vectorstore**: Use network-attached storage for `/vectorstore`
3. **Database**: Move catalog to PostgreSQL for faster queries
4. **CDN**: Cache API responses using CloudFront/Cloudflare

## Compliance

- ✅ Data residency: Keep data in specified region
- ✅ GDPR: Implement data export/deletion endpoints
- ✅ SOC2: Enable audit logging
- ✅ Encryption: Use HTTPS + encryption at rest

## Rollback Plan

```bash
# Tag releases
git tag -a v1.0.0 -m "Release 1.0.0"

# Quick rollback
docker rollback testbot

# Or restart with previous image
docker run -d --name testbot testbot:0.9.0
```

---

**Need help?** Check main README.md or create an issue.
