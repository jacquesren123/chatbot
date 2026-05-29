# Memory Bank - AI Multi-Tenant Chatbot Platform

## Project Overview
Building a scalable B2B SaaS platform that allows businesses to deploy AI-powered chatbots on their websites. Each business gets complete data isolation, conversation history, analytics, and customization capabilities.

**Focus:** Web-based chatbot platform (NOT SMS) where businesses can manage customer conversations, view history, and integrate AI into their customer service workflow.

## ✅ POC COMPLETE - Core Infrastructure Working

### What Was Built

**Architecture:** Microservices-based platform with 6 independent services, event-driven communication via RabbitMQ, multi-tenant SaaS design, provider-agnostic AI layer.

### Services Implemented

1. **API Gateway** (Port 8000) - Multi-tenant routing, health checks, service orchestration
2. **AI Engine** (Port 8001) - Conversational AI with Ollama (llama3.2), OpenAI, and Anthropic support
3. **Qualification Engine** (Port 8003) - Rule-based lead scoring with configurable criteria
4. **Scheduling Service** (Port 8004) - Appointment booking with availability lookup
5. **Workflow Orchestrator** (Port 8005) - Event-driven automation listening to RabbitMQ

**Removed/Deprecated:**
- SMS Gateway (Port 8002) - Not needed for web chatbot platform

### Infrastructure
- **PostgreSQL** - 8 tables (tenants, leads, conversations, messages, appointments, qualification_scores, workflows, workflow_executions)
- **Redis** - Conversation memory (24h TTL, last 10 messages for AI context)
- **RabbitMQ** - Event bus for inter-service communication
- **Docker Compose** - Local development environment

### Tech Stack
- Python 3.11+ with FastAPI
- SQLAlchemy ORM
- LangChain for AI orchestration
- Ollama for free local AI (llama3.2 model)
- aio-pika for async RabbitMQ

## Current Status

### ✅ Working
1. Infrastructure (PostgreSQL, Redis, RabbitMQ) - All running
2. Database Setup - 8 tables created
3. AI Engine - Ollama working, conversation memory in Redis
4. API Gateway - Routes requests to AI Engine
5. Web Test UI - Simple HTML chat interface (test-ui.html)
6. Multi-tenant foundation - Tenant ID in headers

### 🔧 In Progress
1. Database persistence - Adding conversation/message storage to PostgreSQL
2. Conversation history retrieval - Need API endpoints
3. Business dashboard - Not built yet

### ❌ Not Started
1. Embeddable chat widget (production-ready)
2. Business dashboard UI
3. User authentication (JWT)
4. Conversation management UI
5. Analytics dashboard
6. Agent workspace
7. CRM integrations
8. Advanced customization per tenant

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

### Test Web Chat
Open `test-ui.html` in browser

### View Logs
```bash
tail -f logs/ai-engine.log
tail -f logs/api-gateway.log
```

## Configuration

All configuration in `.env` file (copy from `.env.example`):
- Database: `postgresql://chatbot:chatbot_dev@localhost:5432/chatbot_platform`
- Redis: `redis://localhost:6379`
- RabbitMQ: `amqp://chatbot:chatbot_dev@localhost:5672`
- AI provider API keys (optional - using Ollama by default)
- Service ports

## Key Design Decisions

1. **Provider Abstraction** - AI providers abstracted via interface, easy to swap
2. **Event-Driven** - Services communicate via RabbitMQ, not direct HTTP
3. **Stateless Services** - All state in PostgreSQL/Redis
4. **Multi-Tenancy** - Tenant ID in headers, database-level isolation
5. **Lazy Loading** - AI providers only initialized when used
6. **Web-First** - Focus on web chat widget, not SMS

## Data Flow

### Web Chat Flow
1. User types message in chat widget
2. Widget → API Gateway (`/api/v1/chat`)
3. API Gateway → AI Engine (`/chat`)
4. AI Engine:
   - Retrieves conversation history from Redis
   - Generates response using AI provider
   - Saves to Redis (conversation memory)
   - Saves to PostgreSQL (permanent history)
5. Response → API Gateway → Widget
6. Events published to RabbitMQ for workflows

### Conversation Storage
- **Redis**: Last 10 messages for AI context (fast, temporary)
- **PostgreSQL**: All messages forever (permanent, searchable)

## Database Schema

### Core Tables
1. **tenants** - Business accounts
2. **conversations** - Chat sessions (tenant_id, phone_number/user_id, status)
3. **messages** - Individual messages (conversation_id, role, content)
4. **leads** - Qualified leads from conversations
5. **appointments** - Scheduled appointments
6. **qualification_scores** - Lead scoring results
7. **workflows** - Automation workflows
8. **workflow_executions** - Workflow run history

### Key Relationships
- Tenant → Conversations (1:many)
- Conversation → Messages (1:many)
- Conversation → Lead (1:1)
- Lead → Appointments (1:many)

## Files Structure

### Core Services (7 files)
- `services/api-gateway/main.py` - Entry point, routing
- `services/ai_engine/main.py` - Chat orchestration
- `services/ai_engine/providers.py` - AI provider implementations
- `services/ai_engine/memory.py` - Redis conversation memory
- `services/qualification-engine/main.py` - Lead scoring
- `services/scheduling-service/main.py` - Appointment booking
- `services/workflow-orchestrator/main.py` - Event automation

### Shared Infrastructure (14 files)
- `shared/models/` - 6 model files (tenant, lead, conversation, appointment, workflow, __init__)
- `shared/database/` - 4 files (base, session, migrate, __init__)
- `shared/queue/` - 4 files (publisher, consumer, events, __init__)

### Configuration (11 files)
- `README.md` - Quick start guide
- `BUSINESS_REQUIREMENTS.md` - Full platform vision
- `requirements.txt` - Python dependencies
- `.env.example` - Environment template
- `.gitignore`
- `docker-compose.yml` - Infrastructure setup
- `start-all.sh`, `stop-services.sh` - Service management
- `test-ui.html` - Simple web chat interface
- `docs/` - ARCHITECTURE.md, API_EXAMPLES.md, DEPLOYMENT.md

## Issues Fixed During Development

1. Docker permissions - Added user to docker group
2. Package conflict - Uninstalled conflicting "shared" package
3. Anthropic version - Updated to >=0.17.0
4. SQLAlchemy metadata - Renamed to meta_data (reserved word)
5. AI Provider - Added Ollama for free local AI
6. Import errors - Fixed relative imports, added datetime import
7. Service naming - Renamed ai-engine to ai_engine
8. Environment loading - Added python-dotenv
9. ConversationStatus import - Added to shared models exports
10. Database models - Using SQLAlchemy models (not Pydantic) for DB operations

## Current Limitations (POC)

1. **No Dashboard** - No UI for businesses to view conversations
2. **No Authentication** - Basic tenant ID header, no JWT validation
3. **No Widget** - test-ui.html is basic, not production embeddable widget
4. **No History API** - Can't retrieve past conversations via API
5. **No User Management** - No login, signup, team members
6. **No Analytics** - No metrics, charts, insights
7. **No Customization** - Can't configure AI personality per tenant
8. **No Agent Workspace** - No human handoff UI
9. **Google Calendar** - Uses mock availability, OAuth not implemented
10. **Rate Limiting** - Not implemented
11. **Monitoring** - No Prometheus/Grafana
12. **Testing** - No unit tests

## Next Steps (Priority Order)

### Phase 1 - Core Functionality
- [ ] Fix database persistence (conversations + messages)
- [ ] Add conversation history API endpoints
- [ ] Build basic business dashboard (React)
- [ ] Add user authentication (JWT)
- [ ] Create production-ready embeddable widget
- [ ] Add conversation search and filtering

### Phase 2 - Business Features
- [ ] Tenant management (signup, settings)
- [ ] Conversation management UI
- [ ] Basic analytics dashboard
- [ ] Lead qualification UI
- [ ] Appointment scheduling UI
- [ ] Agent workspace (basic)

### Phase 3 - Integrations
- [ ] Google Calendar OAuth
- [ ] CRM integrations (HubSpot, Salesforce)
- [ ] Webhook system
- [ ] Email notifications
- [ ] Slack notifications

### Phase 4 - Scale & Polish
- [ ] Rate limiting per tenant
- [ ] Comprehensive logging and monitoring
- [ ] Unit and integration tests
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Documentation site

## Important Patterns

1. **Services are stateless** - Store state in PostgreSQL/Redis
2. **Use events for inter-service communication** - RabbitMQ
3. **Provider abstraction** - Don't hardcode AI providers
4. **Multi-tenant by default** - Always include tenant_id
5. **Minimal code** - Keep implementations concise
6. **Web-first** - Focus on web chat, not SMS

## API Endpoints

### Current
- `POST /api/v1/chat` - Send message, get AI response
- `GET /health` - Health check

### Needed
- `GET /api/v1/conversations` - List conversations for tenant
- `GET /api/v1/conversations/{id}` - Get conversation details
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages
- `POST /api/v1/conversations/{id}/takeover` - Agent takeover
- `GET /api/v1/analytics` - Get analytics for tenant
- `POST /api/v1/tenants` - Create tenant (signup)
- `PUT /api/v1/tenants/{id}` - Update tenant settings

## Workspace Location
`~/chatbot` (WSL Ubuntu 24.04)

## Last Updated
Pivoted from SMS platform to web chatbot platform. Core infrastructure working, focusing on conversation history, dashboard, and embeddable widget next.
