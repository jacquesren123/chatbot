# Memory Bank - AI Conversational Platform POC

## Project Overview
Built a complete POC for an AI-powered conversational engagement platform focused on SMS-based lead acquisition, qualification, appointment scheduling, and customer lifecycle automation.

## ✅ POC COMPLETE - All Services Working

### What Was Built

**Architecture:** Microservices-based platform with 6 independent services, event-driven communication via RabbitMQ, multi-tenant SaaS design, provider-agnostic AI layer.

### Services Implemented

1. **API Gateway** (Port 8000) - Multi-tenant routing, health checks, service orchestration
2. **AI Engine** (Port 8001) - Conversational AI with Ollama (llama3.2), OpenAI, and Anthropic support
3. **SMS Gateway** (Port 8002) - Twilio integration with webhook handling
4. **Qualification Engine** (Port 8003) - Rule-based lead scoring with configurable criteria
5. **Scheduling Service** (Port 8004) - Appointment booking with availability lookup
6. **Workflow Orchestrator** (Port 8005) - Event-driven automation listening to RabbitMQ

### Infrastructure
- **PostgreSQL** - 8 tables (tenants, leads, conversations, messages, appointments, qualification_scores, workflows, workflow_executions)
- **Redis** - Conversation memory (24h TTL, last 10 messages)
- **RabbitMQ** - Event bus for inter-service communication
- **Docker Compose** - Local development environment

### Tech Stack
- Python 3.11+ with FastAPI
- SQLAlchemy ORM
- LangChain for AI orchestration
- Ollama for free local AI (llama3.2 model)
- Twilio for SMS
- aio-pika for async RabbitMQ

## Quick Start Commands

### Start Infrastructure
```bash
docker-compose up -d
```

### Start All Services
```bash
./start-all.sh
```

### Stop All Services
```bash
./stop-services.sh
```

### Check Health
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
tail -f logs/sms-gateway.log
tail -f logs/ai-engine.log
```

### Start Ngrok (for SMS webhook)
```bash
ngrok http 8002
```

## Configuration

All configuration in `.env` file (copy from `.env.example`):
- Database, Redis, RabbitMQ URLs
- Twilio credentials (Account SID, Auth Token, Phone Number)
- AI provider API keys (optional - using Ollama by default)
- Service ports

## Testing Progress

### ✅ Completed
1. Infrastructure (PostgreSQL, Redis, RabbitMQ) - All running and verified
2. Database Setup - 8 tables created successfully
3. AI Engine - Tested with Ollama (free local AI), conversation memory working
4. Qualification Engine - Lead scoring tested (100% score achieved)
5. Scheduling Service - Availability lookup working (9am-5pm slots)
6. Workflow Orchestrator - Running and listening to events
7. API Gateway - All services integrated, health checks working
8. SMS Gateway - Webhook tested, receives and processes messages

### SMS Testing Note
- Webhook successfully receives SMS from Twilio
- AI processes messages and generates responses
- Twilio trial accounts require phone number verification
- Production deployment requires Twilio account upgrade ($20 minimum)

## Key Design Decisions

1. **Provider Abstraction** - AI providers abstracted via interface, easy to swap
2. **Event-Driven** - Services communicate via RabbitMQ, not direct HTTP
3. **Stateless Services** - All state in PostgreSQL/Redis
4. **Multi-Tenancy** - Tenant ID in headers, database-level isolation
5. **Lazy Loading** - AI providers only initialized when used

## Default Qualification Rules

```python
{
    "has_budget": {"weight": 0.3, "required": True},
    "has_timeline": {"weight": 0.2, "required": False},
    "decision_maker": {"weight": 0.3, "required": True},
    "need_identified": {"weight": 0.2, "required": True}
}
```
Threshold: 0.7 (70%)

## Data Flow Examples

### Inbound SMS Flow
1. SMS → Twilio → Webhook (`/webhook/twilio`)
2. SMS Gateway publishes `MESSAGE_RECEIVED` event
3. SMS Gateway calls AI Engine `/chat`
4. AI Engine generates response using conversation history from Redis
5. SMS Gateway sends response via Twilio
6. SMS Gateway publishes `MESSAGE_SENT` event

### Lead Qualification Flow
1. Qualification Engine receives `/qualify` request
2. Evaluates conversation against rules
3. Calculates weighted score
4. If qualified (≥0.7), publishes `LEAD_QUALIFIED` event
5. Workflow Orchestrator triggers follow-up

## Files Structure

### Core Services (8 files)
- `services/api-gateway/main.py`
- `services/ai_engine/main.py`
- `services/ai_engine/providers.py`
- `services/ai_engine/memory.py`
- `services/sms-gateway/main.py`
- `services/qualification-engine/main.py`
- `services/scheduling-service/main.py`
- `services/workflow-orchestrator/main.py`

### Shared Infrastructure (14 files)
- `shared/models/` - 6 model files (tenant, lead, conversation, appointment, workflow, __init__)
- `shared/database/` - 4 files (base, session, migrate, __init__)
- `shared/queue/` - 4 files (publisher, consumer, events, __init__)

### Configuration (10 files)
- `README.md`, `requirements.txt`, `.env.example`, `.gitignore`
- `docker-compose.yml`
- `start-all.sh`, `stop-services.sh`
- `docs/` - ARCHITECTURE.md, API_EXAMPLES.md, DEPLOYMENT.md

## Issues Fixed During Development

1. Docker permissions - Added user to docker group
2. Package conflict - Uninstalled conflicting "shared" package
3. Anthropic version - Updated to >=0.17.0
4. SQLAlchemy metadata - Renamed to meta_data (reserved word)
5. AI Provider - Added Ollama for free local AI
6. Import errors - Fixed relative imports, added datetime import
7. Service naming - Renamed ai-engine to ai_engine
8. Twilio credentials - Fixed Account SID vs API Key confusion
9. Environment loading - Added python-dotenv
10. Ngrok setup - Installed for webhook exposure

## Known Limitations (POC)

1. Google Calendar - Uses mock availability, OAuth not implemented
2. Authentication - Basic tenant ID header, no JWT validation
3. Rate Limiting - Not implemented
4. Monitoring - No Prometheus/Grafana
5. Testing - No unit tests
6. CRM Integration - Not implemented
7. Agent Dashboard - Not built
8. Vector Database - Not included

## Production Readiness Checklist

- [ ] Implement OAuth flows (Google Calendar)
- [ ] Add JWT authentication
- [ ] Implement rate limiting per tenant
- [ ] Add comprehensive logging and monitoring
- [ ] Build admin dashboard
- [ ] Add CRM integrations (HubSpot, Salesforce)
- [ ] Implement vector database for knowledge base
- [ ] Add A/B testing for prompts
- [ ] Build agent workspace
- [ ] Add voice channel support
- [ ] Implement visual workflow builder
- [ ] Add comprehensive test suite
- [ ] Deploy to production server
- [ ] Set up CI/CD pipeline
- [ ] Configure proper domain and SSL

## Important Patterns

1. Services are stateless - Store state in PostgreSQL/Redis
2. Use events for inter-service communication
3. Provider abstraction - Don't hardcode AI providers
4. Multi-tenant by default - Always include tenant_id
5. Minimal code - Keep implementations concise

## Workspace Location
`~/chatbot` (WSL Ubuntu 24.04)

## Last Updated
POC Complete - All services tested and working. SMS infrastructure functional, blocked only by Twilio trial account limitations.
