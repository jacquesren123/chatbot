# Deployment Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Twilio account (for SMS)
- OpenAI or Anthropic API key
- Google Cloud project (for Calendar API)

## Local Development Setup

### 1. Clone and Setup Environment

```bash
cd ~/chatbot
cp .env.example .env
```

Edit `.env` with your credentials:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, management UI: 15672)

### 4. Initialize Database

```bash
python shared/database/migrate.py
```

### 5. Start Services

```bash
chmod +x start-services.sh
./start-services.sh
```

Services will be available at:
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs
- AI Engine: http://localhost:8001
- SMS Gateway: http://localhost:8002
- Qualification Engine: http://localhost:8003
- Scheduling Service: http://localhost:8004
- Workflow Orchestrator: http://localhost:8005

### 6. Configure Twilio Webhook

In Twilio Console, set webhook URL to:
```
https://your-domain.com/webhook/twilio
```

Use ngrok for local testing:
```bash
ngrok http 8002
```

## Testing

### Test AI Engine
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test123",
    "tenant_id": "tenant1",
    "message": "Hi, I need help",
    "context": {}
  }'
```

### Test SMS Send
```bash
curl -X POST http://localhost:8002/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Test message",
    "tenant_id": "tenant1"
  }'
```

### Test Qualification
```bash
curl -X POST http://localhost:8003/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead123",
    "tenant_id": "tenant1",
    "conversation_history": [
      {"role": "user", "content": "I have a budget of $10k"},
      {"role": "assistant", "content": "Great! When are you looking to start?"}
    ],
    "lead_attributes": {"is_decision_maker": true}
  }'
```

## Production Deployment

### AWS Deployment (Recommended)

1. **ECS/Fargate** for microservices
2. **RDS PostgreSQL** for database
3. **ElastiCache Redis** for caching
4. **Amazon MQ** for RabbitMQ
5. **Application Load Balancer** for routing
6. **CloudWatch** for monitoring

### Docker Compose Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

## Environment Variables

Required for production:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `JWT_SECRET`: Strong random secret for authentication

## Monitoring

Access RabbitMQ Management UI:
```
http://localhost:15672
Username: chatbot
Password: chatbot_dev
```

## Troubleshooting

### Services won't start
- Check Docker is running: `docker ps`
- Check logs: `docker-compose logs`
- Verify ports are available: `netstat -an | grep LISTEN`

### Database connection errors
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check DATABASE_URL in .env
- Test connection: `psql $DATABASE_URL`

### AI responses not working
- Verify API keys in .env
- Check AI Engine logs: `docker logs ai-engine`
- Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### SMS not sending
- Verify Twilio credentials
- Check Twilio account balance
- Review SMS Gateway logs
