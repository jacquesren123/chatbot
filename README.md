# AI-Powered Multi-Tenant Chatbot Platform

A scalable B2B SaaS platform that allows businesses to deploy AI-powered chatbots on their websites.

## Quick Start

```bash
# Start infrastructure
docker-compose up -d

# Start all services
./start-all.sh

# Check health
curl http://localhost:8000/health

# Open test chat UI
explorer.exe chat.html  
```

## Test Conversation

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-Tenant-Id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Hello"}'
```

## Architecture Overview

Multi-tenant chatbot platform with microservices architecture for scalable AI-powered customer conversations.

### Services

- **API Gateway** (Port 8000) - Multi-tenant routing, authentication, rate limiting
- **AI Engine** (Port 8001) - Provider-agnostic conversational AI (OpenAI, Anthropic, Ollama)
- **Qualification Engine** (Port 8003) - Rule-based + AI-powered lead scoring
- **Scheduling Service** (Port 8004) - Calendar integration for appointment booking
- **Workflow Orchestrator** (Port 8005) - Event-driven automation engine

### Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL (multi-tenant)
- **Cache/Session**: Redis
- **Message Queue**: RabbitMQ
- **AI**: OpenAI/Anthropic/Ollama with LangChain
- **Deployment**: Docker + Docker Compose

## Features

### Current (POC)
- ✅ Multi-tenant architecture
- ✅ AI-powered conversations with memory
- ✅ Provider-agnostic AI (swap OpenAI/Anthropic/Ollama)
- ✅ Conversation history (Redis + PostgreSQL)
- ✅ Event-driven workflows
- ✅ Lead qualification engine
- ✅ Appointment scheduling
- ✅ Simple web chat UI

### Planned
- [ ] Business dashboard
- [ ] Embeddable chat widget
- [ ] User authentication (JWT)
- [ ] Conversation management UI
- [ ] Analytics dashboard
- [ ] Agent workspace
- [ ] CRM integrations
- [ ] Advanced customization per tenant

## Project Structure

```
chatbot/
├── services/
│   ├── api-gateway/          # Entry point, routing
│   ├── ai_engine/            # Conversational AI
│   ├── qualification-engine/ # Lead qualification
│   ├── scheduling-service/   # Calendar management
│   └── workflow-orchestrator/# Automation workflows
├── shared/
│   ├── database/             # Schema, migrations
│   ├── queue/                # Message queue utilities
│   └── models/               # Shared data models
├── test-ui.html              # Simple web chat interface
└── docs/                     # Architecture docs
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

## Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://chatbot:chatbot_dev@localhost:5432/chatbot_platform

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_URL=amqp://chatbot:chatbot_dev@localhost:5672

# AI Providers (optional - using Ollama by default)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## API Endpoints

### Chat
```bash
POST /api/v1/chat
Headers: X-Tenant-Id: tenant1
Body: {"phone_number": "user123", "message": "Hello"}
```

### Health Check
```bash
GET /health
```

## Development

```bash
# View logs
tail -f logs/api-gateway.log
tail -f logs/ai-engine.log

# Check database
docker exec -it chatbot_postgres_1 psql -U chatbot -d chatbot_platform

# Check Redis
docker exec -it chatbot_redis_1 redis-cli

# Stop services
./stop-services.sh
```

## Documentation

- [Business Requirements](BUSINESS_REQUIREMENTS.md) - Full platform vision
- [Architecture](docs/ARCHITECTURE.md) - System design
- [API Examples](docs/API_EXAMPLES.md) - API usage
- [Deployment](docs/DEPLOYMENT.md) - Production deployment

## License

MIT
