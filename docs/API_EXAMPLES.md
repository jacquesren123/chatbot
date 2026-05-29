# API Examples

## Authentication

All API requests require a tenant ID header:
```
X-Tenant-Id: your-tenant-id
```

## Chat API

### Send a message
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant1" \
  -d '{
    "phone_number": "+1234567890",
    "message": "Hi, I want to learn more about your services"
  }'
```

Response:
```json
{
  "response": "Hello! I'd be happy to help you learn about our services. What specifically are you interested in?",
  "intent": "general_inquiry",
  "should_escalate": false,
  "metadata": {}
}
```

## SMS API

### Send SMS
```bash
curl -X POST http://localhost:8000/api/v1/sms/send \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant1" \
  -d '{
    "to": "+1234567890",
    "message": "Thanks for your interest! A team member will contact you soon."
  }'
```

## Scheduling API

### Get availability
```bash
curl -X GET "http://localhost:8000/api/v1/availability?start_date=2024-01-20T00:00:00Z&end_date=2024-01-27T00:00:00Z" \
  -H "X-Tenant-Id: tenant1"
```

Response:
```json
[
  {
    "start": "2024-01-20T09:00:00Z",
    "end": "2024-01-20T09:30:00Z",
    "available": true
  },
  {
    "start": "2024-01-20T09:30:00Z",
    "end": "2024-01-20T10:00:00Z",
    "available": true
  }
]
```

## Complete Conversation Flow

### 1. User sends initial message
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant1" \
  -d '{
    "phone_number": "+1234567890",
    "message": "I need help with my project"
  }'
```

### 2. AI qualifies the lead
```bash
curl -X POST http://localhost:8003/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead123",
    "tenant_id": "tenant1",
    "conversation_history": [
      {"role": "user", "content": "I need help with my project"},
      {"role": "assistant", "content": "I can help! What's your budget?"},
      {"role": "user", "content": "Around $10,000"},
      {"role": "assistant", "content": "Great! When do you need to start?"},
      {"role": "user", "content": "As soon as possible"}
    ],
    "lead_attributes": {
      "is_decision_maker": true
    }
  }'
```

### 3. Schedule appointment
```bash
curl -X POST http://localhost:8004/book \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant1",
    "lead_id": "lead123",
    "conversation_id": "conv123",
    "start_time": "2024-01-20T14:00:00Z",
    "duration_minutes": 30,
    "attendee_phone": "+1234567890",
    "attendee_email": "user@example.com"
  }'
```

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "gateway": "healthy",
  "services": {
    "ai_engine": "healthy",
    "sms_gateway": "healthy",
    "qualification_engine": "healthy",
    "scheduling_service": "healthy"
  }
}
```
