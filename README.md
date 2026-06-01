# AI Business Concierge Platform

A scalable B2B SaaS platform for deploying AI-powered business assistants with custom knowledge bases.

## 🚀 Quick Start

```bash
# 1. Start infrastructure (PostgreSQL, Redis, RabbitMQ)
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Ollama (for free local AI)
# Visit: https://ollama.ai
ollama pull llama3.1:8b

# 4. Start all services
./start-all.sh

# 5. Open web interfaces
explorer.exe chat.html      # Chat interface
explorer.exe upload.html    # Document upload
explorer.exe dashboard.html # Analytics dashboard
```

**📖 New to the project?** See [SETUP.md](SETUP.md) for detailed setup instructions.

**⚡ Need quick commands?** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks.

## 📚 RAG Knowledge Base

Upload your business documents and the AI will answer questions using your specific information.

### How It Works

1. **Upload Documents** - PDF, DOCX, or TXT files via upload.html
2. **Automatic Processing** - Text extraction and chunking (500 chars)
3. **Redis Storage** - Chunks stored with multi-tenant isolation
4. **Smart Retrieval** - Keyword search finds relevant information
5. **AI Response** - llama3.1:8b uses your data to answer questions

### Example

```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-Tenant-Id: tenant1" \
  -F "file=@business-info.pdf"

# Chat with your data
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "user123", "message": "What are your prices?"}'
```

### Upgrade to Vector Search

For semantic understanding (not just keyword matching):

```bash
# Uncomment in requirements.txt:
# pinecone-client==3.0.0

# Add to .env:
OPENAI_API_KEY=sk-your-key
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-west1-gcp
```

## 🏗️ Architecture

### Services

- **API Gateway** (Port 8000) - Multi-tenant routing, document upload, analytics
- **AI Engine** (Port 8001) - Conversational AI with RAG integration
- **Qualification Engine** (Port 8003) - Lead scoring
- **Scheduling Service** (Port 8004) - Appointment booking
- **Workflow Orchestrator** (Port 8005) - Event automation

### Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL (conversations, messages, users)
- **Cache**: Redis (sessions, RAG storage)
- **Message Queue**: RabbitMQ (async workflows)
- **AI Models**: 
  - Ollama (llama3.1:8b) - Free, local, good for RAG
  - OpenAI (GPT-4) - Best quality, paid
  - Anthropic (Claude) - High quality, paid
- **RAG System**: Redis-backed keyword search (vector search coming)
- **Deployment**: Docker + Docker Compose

## ✨ Key Features

### Current (Production-Ready POC)
- ✅ **RAG Knowledge Base** - Upload PDFs/DOCX/TXT, AI answers using your business data
- ✅ **Multi-tenant Architecture** - Complete data isolation per business
- ✅ **AI-powered Conversations** - Natural language understanding with memory
- ✅ **Provider-agnostic AI** - Swap between OpenAI/Anthropic/Ollama (free local)
- ✅ **Conversation History** - Redis + PostgreSQL persistence
- ✅ **Web Interfaces** - Chat UI, document upload, analytics dashboard
- ✅ **Event-driven Workflows** - RabbitMQ for async processing
- ✅ **Lead Qualification** - AI-powered lead scoring
- ✅ **Appointment Scheduling** - Calendar integration framework

### Coming Soon
- [ ] Vector Search (Pinecone/Chroma) - Semantic understanding
- [ ] Embeddable Widget - One-line JavaScript embed
- [ ] CRM Integrations - HubSpot, Salesforce
- [ ] Human Handoff - Slack/Email notifications
- [ ] Advanced Analytics - Conversation insights

## 📁 Project Structure

```
chatbot/
├── services/
│   ├── api-gateway/          # Entry point, routing, document upload
│   ├── ai_engine/            # Conversational AI + RAG
│   │   ├── main.py           # Chat orchestration
│   │   ├── providers.py      # AI providers (OpenAI/Anthropic/Ollama)
│   │   ├── memory.py         # Redis conversation memory
│   │   └── rag.py            # RAG system (Redis-backed)
│   ├── qualification-engine/ # Lead scoring
│   ├── scheduling-service/   # Calendar management
│   └── workflow-orchestrator/# Automation workflows
├── shared/
│   ├── database/             # Schema, migrations
│   ├── queue/                # RabbitMQ utilities
│   └── models/               # SQLAlchemy models
├── chat.html                 # Chat interface
├── upload.html               # Document upload UI
├── dashboard.html            # Analytics dashboard
├── sample-business-info.txt  # Test data
└── docs/                     # Documentation
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start infrastructure
docker-compose up -d

# Run migrations
python shared/database/migrate.py

# Start services
./start-all.sh
```

## ⚙️ Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://chatbot:chatbot_dev@localhost:5432/chatbot_platform

# Redis (also used for RAG storage)
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_URL=amqp://chatbot:chatbot_dev@localhost:5672

# AI Providers
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b  # Free local model

# Optional: For better quality (paid)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: For vector search upgrade
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-west1-gcp
```

## 💻 API Endpoints

### Chat
```bash
POST /api/v1/chat
Headers: 
  X-Tenant-Id: tenant1
  Content-Type: application/json
Body: 
  {
    "phone_number": "user123",
    "message": "What are your services?",
    "provider": "ollama"  # Optional: ollama, openai, anthropic
  }
```

### Document Management
```bash
# Upload document
POST /api/v1/documents/upload
Headers: X-Tenant-Id: tenant1
Body: multipart/form-data with file

# List documents
GET /api/v1/documents
Headers: X-Tenant-Id: tenant1

# Delete document
DELETE /api/v1/documents/{doc_id}
Headers: X-Tenant-Id: tenant1

# Test RAG search
GET /api/v1/documents/search?query=pricing
Headers: X-Tenant-Id: tenant1
```

### Analytics
```bash
# Get conversation analytics
GET /api/v1/analytics
Headers: X-Tenant-Id: tenant1

# List conversations
GET /api/v1/conversations
Headers: X-Tenant-Id: tenant1

# Get conversation messages
GET /api/v1/conversations/{id}/messages
Headers: X-Tenant-Id: tenant1
```

### Health Check
```bash
GET /health
```

## 🔧 Development

### View Logs
```bash
tail -f logs/api-gateway.log
tail -f logs/ai-engine.log
```

### Database Access
```bash
# PostgreSQL
docker exec -it chatbot_postgres_1 psql -U chatbot -d chatbot_platform

# Redis
docker exec -it chatbot_redis_1 redis-cli

# Check RAG storage
redis-cli
> KEYS rag:*
> GET rag:765d11bd-3a59-53fd-89ae-f201187a7cf4:doc-id
```

### Testing
```bash
# Test RAG retrieval
curl "http://localhost:8000/api/v1/documents/search?query=pricing" \
  -H "X-Tenant-Id: tenant1"

# Test chat with RAG
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "test", "message": "What are your prices?"}'
```

### Stop Services
```bash
./stop-services.sh
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions with troubleshooting
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and API endpoints
- **[BUSINESS_REQUIREMENTS.md](BUSINESS_REQUIREMENTS.md)** - Full platform vision
- **[Memory Bank](.amazonq/rules/memory-bank.md)** - Project status and decisions
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[API Examples](docs/API_EXAMPLES.md)** - API usage examples

## 🚀 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guide.

## 👥 Target Use Cases

1. **Digital Agencies** - White-label AI assistants for clients
2. **SaaS Companies** - Customer support automation
3. **Professional Services** - Appointment booking automation
4. **E-commerce** - Product recommendations with custom catalog
5. **Real Estate** - Property inquiry automation

## 📊 Roadmap

- [x] Phase 1: RAG Knowledge Base (COMPLETE)
- [ ] Phase 2: Vector Search (Pinecone/Chroma)
- [ ] Phase 3: Embeddable Widget
- [ ] Phase 4: CRM Integrations
- [ ] Phase 5: Human Handoff System

## 📝 License

MIT
