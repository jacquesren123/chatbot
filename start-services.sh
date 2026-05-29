#!/bin/bash

echo "Starting AI Conversational Platform Services..."

# Start infrastructure
echo "Starting infrastructure (PostgreSQL, Redis, RabbitMQ)..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for infrastructure to be ready..."
sleep 10

# Start microservices
echo "Starting API Gateway..."
cd services/api-gateway && uvicorn main:app --host 0.0.0.0 --port 8000 &

echo "Starting AI Engine..."
cd ../ai-engine && uvicorn main:app --host 0.0.0.0 --port 8001 &

echo "Starting SMS Gateway..."
cd ../sms-gateway && uvicorn main:app --host 0.0.0.0 --port 8002 &

echo "Starting Qualification Engine..."
cd ../qualification-engine && uvicorn main:app --host 0.0.0.0 --port 8003 &

echo "Starting Scheduling Service..."
cd ../scheduling-service && uvicorn main:app --host 0.0.0.0 --port 8004 &

echo "Starting Workflow Orchestrator..."
cd ../workflow-orchestrator && uvicorn main:app --host 0.0.0.0 --port 8005 &

echo ""
echo "All services started!"
echo "API Gateway: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop all services, run: ./stop-services.sh"
