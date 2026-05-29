# AI-Powered Conversational Engagement Platform - POC

## Architecture Overview

This POC implements a microservices-based conversational AI platform for SMS lead engagement, qualification, and appointment scheduling.

### Services

- **API Gateway** - Multi-tenant routing, authentication, rate limiting
- **AI Engine** - Provider-agnostic conversational AI (OpenAI, Anthropic)
- **SMS Gateway** - Twilio integration with webhook handling
- **Qualification Engine** - Rule-based + AI-powered lead scoring
- **Scheduling Service** - Google Calendar integration
- **Workflow Orchestrator** - Event-driven automation engine

### Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL (multi-tenant)
- **Cache/Session**: Redis
- **Message Queue**: RabbitMQ
- **AI**: OpenAI/Anthropic with LangChain
- **SMS**: Twilio
- **Scheduling**: Google Calendar API
- **Deployment**: Docker + Docker Compose

## Quick Start

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
./start-services.sh
```

## Project Structure

```
chatbot/
├── services/
│   ├── api-gateway/          # Entry point, routing
│   ├── ai-engine/            # Conversational AI
│   ├── sms-gateway/          # SMS provider integration
│   ├── qualification-engine/ # Lead qualification
│   ├── scheduling-service/   # Calendar management
│   └── workflow-orchestrator/# Automation workflows
├── shared/
│   ├── database/             # Schema, migrations
│   ├── queue/                # Message queue utilities
│   └── models/               # Shared data models
└── docs/                     # Architecture docs
```
