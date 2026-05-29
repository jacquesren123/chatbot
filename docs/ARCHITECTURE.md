# System Architecture

## Overview

This platform implements a microservices architecture for AI-powered conversational engagement via SMS.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
│ (SMS/API)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│          API Gateway (8000)             │
│  - Multi-tenant routing                 │
│  - Authentication                       │
│  - Rate limiting                        │
└──────┬──────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│AI Engine │   │   SMS    │   │Qualific. │   │Scheduling│   │Workflow  │
│  (8001)  │   │ Gateway  │   │  Engine  │   │ Service  │   │Orchestr. │
│          │   │  (8002)  │   │  (8003)  │   │  (8004)  │   │  (8005)  │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │              │
     └──────────────┴──────────────┴──────────────┴──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │PostgreSQL│   │  Redis   │   │RabbitMQ  │
              │  (5432)  │   │  (6379)  │   │  (5672)  │
              └──────────┘   └──────────┘   └──────────┘
```

## Service Responsibilities

### API Gateway (Port 8000)
- Entry point for all external requests
- Multi-tenant authentication and routing
- Rate limiting and request validation
- Service discovery and load balancing

### AI Engine (Port 8001)
- Provider-agnostic conversational AI
- Supports OpenAI and Anthropic
- Conversation memory management (Redis)
- Intent detection and context handling
- Escalation detection

### SMS Gateway (Port 8002)
- Twilio integration
- Webhook handling for inbound messages
- Outbound message delivery
- Message queuing and retry logic

### Qualification Engine (Port 8003)
- Rule-based lead qualification
- AI-assisted scoring
- Configurable criteria per tenant
- Lead status management

### Scheduling Service (Port 8004)
- Google Calendar integration
- Availability lookup
- Appointment booking
- Reminder workflows

### Workflow Orchestrator (Port 8005)
- Event-driven automation
- Multi-step workflow execution
- Follow-up campaigns
- Escalation handling

## Data Flow

### Inbound SMS Flow
1. SMS received by Twilio → Webhook to SMS Gateway
2. SMS Gateway publishes MESSAGE_RECEIVED event
3. AI Engine processes message with conversation history
4. AI Engine generates response
5. SMS Gateway sends response via Twilio
6. Qualification Engine evaluates lead (if applicable)
7. Workflow Orchestrator triggers follow-up actions

### Appointment Booking Flow
1. User requests appointment via SMS
2. AI Engine detects scheduling intent
3. Scheduling Service queries availability
4. AI Engine presents options to user
5. User selects time slot
6. Scheduling Service books in Google Calendar
7. APPOINTMENT_SCHEDULED event published
8. Workflow Orchestrator sends confirmation + reminders

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (multi-tenant schema)
- **Cache**: Redis (conversation memory, sessions)
- **Message Queue**: RabbitMQ (event-driven architecture)
- **AI**: LangChain + OpenAI/Anthropic
- **SMS**: Twilio
- **Calendar**: Google Calendar API
- **Deployment**: Docker + Docker Compose

## Scalability Considerations

### Horizontal Scaling
- All services are stateless (except Redis for memory)
- Can deploy multiple instances behind load balancer
- Database connection pooling configured

### Event-Driven Architecture
- RabbitMQ enables async processing
- Services communicate via events, not direct calls
- Decoupled services for independent scaling

### Multi-Tenancy
- Tenant isolation at database level
- Per-tenant configuration and rate limits
- Tenant-specific AI models and workflows

## Security

- API key authentication per tenant
- Environment-based secrets management
- Database connection encryption
- Rate limiting per tenant
- Input validation and sanitization

## Monitoring & Observability

Future implementation:
- Prometheus metrics
- Grafana dashboards
- Distributed tracing (Jaeger)
- Centralized logging (ELK stack)
- AI conversation analytics

## Future Enhancements

1. **Omnichannel Support**: WhatsApp, Email, Voice
2. **Visual Workflow Builder**: No-code automation
3. **Advanced Analytics**: Conversion tracking, A/B testing
4. **CRM Integrations**: HubSpot, Salesforce, etc.
5. **Agent Dashboard**: Live conversation monitoring
6. **Voice AI**: Twilio Voice integration
7. **Vector Database**: Semantic search for knowledge base
