# Quick Reference Card

## 🚀 Start/Stop

```bash
# Start everything
docker-compose up -d && ./start-all.sh

# Stop everything
./stop-services.sh && docker-compose down

# Restart AI Engine only
pkill -f "ai_engine/main.py" && nohup python -m services.ai_engine.main > logs/ai-engine.log 2>&1 &
```

## 📁 File Locations

- **Chat UI**: `chat.html`
- **Upload UI**: `upload.html`
- **Dashboard**: `dashboard.html`
- **Logs**: `logs/api-gateway.log`, `logs/ai-engine.log`
- **Config**: `.env`
- **Sample Data**: `sample-business-info.txt`

## 🔌 API Endpoints

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-Tenant-Id: tenant1" \
  -F "file=@your-file.pdf"
```

### Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "user123", "message": "Hello"}'
```

### List Documents
```bash
curl http://localhost:8000/api/v1/documents \
  -H "X-Tenant-Id: tenant1"
```

### Test RAG Search
```bash
curl "http://localhost:8000/api/v1/documents/search?query=pricing" \
  -H "X-Tenant-Id: tenant1"
```

### Analytics
```bash
curl http://localhost:8000/api/v1/analytics \
  -H "X-Tenant-Id: tenant1"
```

## 🔍 Debugging

### Check Services
```bash
# Health check
curl http://localhost:8000/health

# Check if services are running
ps aux | grep python

# View logs
tail -f logs/ai-engine.log
```

### Check Database
```bash
# PostgreSQL
docker exec -it chatbot_postgres_1 psql -U chatbot -d chatbot_platform

# List conversations
SELECT * FROM conversations;

# List messages
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

### Check Redis
```bash
# Connect to Redis
docker exec -it chatbot_redis_1 redis-cli

# Check RAG documents
KEYS rag:*

# Get document
GET rag:765d11bd-3a59-53fd-89ae-f201187a7cf4:doc-id

# Check conversation memory
KEYS conversation:*
```

## 🤖 AI Models

### Current (Free)
- **llama3.1:8b** - Best free model for RAG
- Size: 4.9GB
- Good instruction following

### Alternatives

```bash
# Try different models
ollama pull mistral
ollama pull llama3.2

# Change in .env
OLLAMA_MODEL=mistral
```

### Paid (Better Quality)

```bash
# OpenAI (best)
OPENAI_API_KEY=sk-proj-your-key

# Use in request
{"message": "Hello", "provider": "openai"}

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
{"message": "Hello", "provider": "anthropic"}
```

## 📊 Ports

- **8000** - API Gateway
- **8001** - AI Engine
- **8003** - Qualification Engine
- **8004** - Scheduling Service
- **8005** - Workflow Orchestrator
- **5432** - PostgreSQL
- **6379** - Redis
- **5672** - RabbitMQ
- **11434** - Ollama

## 🐛 Common Issues

### "Context length: 0 chars"
- Document not uploaded
- Wrong tenant ID
- Redis not running

**Fix:**
```bash
# Check documents
curl http://localhost:8000/api/v1/documents -H "X-Tenant-Id: tenant1"

# Re-upload
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-Tenant-Id: tenant1" \
  -F "file=@sample-business-info.txt"
```

### AI Gives Wrong Answers
- Using llama3.2 (too small)
- Temperature too high
- Weak prompt

**Fix:**
```bash
# Switch to llama3.1:8b
ollama pull llama3.1:8b

# Update .env
OLLAMA_MODEL=llama3.1:8b

# Restart AI Engine
pkill -f "ai_engine" && nohup python -m services.ai_engine.main > logs/ai-engine.log 2>&1 &
```

### Port Already in Use
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

## 📝 Testing Checklist

- [ ] Infrastructure running: `docker ps`
- [ ] Services started: `ps aux | grep python`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Document uploaded: Check upload.html
- [ ] RAG search works: Test in upload.html
- [ ] Chat works: Test in chat.html
- [ ] AI uses document data (not hallucinating)

## 🎯 Next Steps

1. Upload your business documents
2. Test with real questions
3. Customize chat.html branding
4. Deploy to production
5. Upgrade to vector search (Pinecone)
6. Add embeddable widget
