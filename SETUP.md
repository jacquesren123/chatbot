# Setup Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Ollama (for free local AI)

## Step-by-Step Setup

### 1. Install Ollama

```bash
# Visit https://ollama.ai and install for your OS

# Pull the recommended model
ollama pull llama3.1:8b
```

### 2. Clone and Setup Environment

```bash
# Navigate to project
cd ~/chatbot

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional)
nano .env
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL, Redis, RabbitMQ
docker-compose up -d

# Verify containers are running
docker ps
```

### 4. Install Python Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Run migrations
python shared/database/migrate.py
```

### 6. Start Services

```bash
# Start all microservices
./start-all.sh

# Check logs
tail -f logs/api-gateway.log
tail -f logs/ai-engine.log
```

### 7. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"gateway": "healthy", "services": {...}}
```

### 8. Open Web Interfaces

```bash
# On Windows WSL
explorer.exe chat.html
explorer.exe upload.html
explorer.exe dashboard.html

# On Linux/Mac
xdg-open chat.html
open chat.html
```

## Testing RAG System

### 1. Upload a Document

1. Open `upload.html` in browser
2. Drag & drop `sample-business-info.txt`
3. Wait for "Document processed successfully with X chunks"

### 2. Test Chat

1. Open `chat.html` in browser
2. Ask: "What is your company name and pricing?"
3. AI should respond with ACME Digital Solutions and exact prices

### 3. Test via API

```bash
# Upload document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-Tenant-Id: tenant1" \
  -F "file=@sample-business-info.txt"

# Test RAG search
curl "http://localhost:8000/api/v1/documents/search?query=pricing" \
  -H "X-Tenant-Id: tenant1"

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "test", "message": "What are your prices?"}'
```

## Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
lsof -i :8000  # API Gateway
lsof -i :8001  # AI Engine
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill existing processes
pkill -f "api-gateway"
pkill -f "ai_engine"
```

### Ollama Not Working

```bash
# Check Ollama is running
ollama list

# Test Ollama
ollama run llama3.1:8b "Hello"

# Check Ollama URL in .env
OLLAMA_URL=http://localhost:11434
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check connection
docker exec -it chatbot_postgres_1 psql -U chatbot -d chatbot_platform
```

### Redis Connection Error

```bash
# Check Redis is running
docker ps | grep redis

# Test Redis
docker exec -it chatbot_redis_1 redis-cli ping
# Should return: PONG

# Check RAG data
docker exec -it chatbot_redis_1 redis-cli
> KEYS rag:*
```

### AI Gives Wrong Answers

This usually means:
1. Document not uploaded correctly
2. Wrong AI model (use llama3.1:8b, not llama3.2)
3. RAG context not being retrieved

```bash
# Check if document is in Redis
curl "http://localhost:8000/api/v1/documents" -H "X-Tenant-Id: tenant1"

# Test RAG search directly
curl "http://localhost:8000/api/v1/documents/search?query=test" \
  -H "X-Tenant-Id: tenant1"

# Check AI Engine logs
tail -f logs/ai-engine.log
# Look for "Context length: X chars" - should be > 0
```

## Upgrading to OpenAI (Better Quality)

```bash
# 1. Get API key from https://platform.openai.com/api-keys

# 2. Add to .env
OPENAI_API_KEY=sk-proj-your-key-here

# 3. Restart services
./stop-services.sh
./start-all.sh

# 4. Use OpenAI in chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "test",
    "message": "What are your prices?",
    "provider": "openai"
  }'
```

## Next Steps

1. Upload your own business documents (PDFs, DOCX, TXT)
2. Test with real customer questions
3. Customize chat.html with your branding
4. Deploy to production (see DEPLOYMENT.md)
5. Upgrade to vector search for better accuracy

## Support

- Check logs in `logs/` directory
- Review [Memory Bank](.amazonq/rules/memory-bank.md) for project status
- See [BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md) for full vision
