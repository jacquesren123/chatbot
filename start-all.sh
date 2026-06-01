#!/bin/bash

cd ~/chatbot
source venv/bin/activate

echo "Starting all microservices..."

# Start AI Engine
cd services/ai_engine
PYTHONPATH=../.. nohup uvicorn main:app --host 0.0.0.0 --port 8001 > ../../logs/ai-engine.log 2>&1 &
echo "AI Engine started on port 8001 (PID: $!)"

# Start Qualification Engine
cd ../qualification-engine
PYTHONPATH=../.. nohup uvicorn main:app --host 0.0.0.0 --port 8003 > ../../logs/qualification-engine.log 2>&1 &
echo "Qualification Engine started on port 8003 (PID: $!)"

# Start Scheduling Service
cd ../scheduling-service
PYTHONPATH=../.. nohup uvicorn main:app --host 0.0.0.0 --port 8004 > ../../logs/scheduling-service.log 2>&1 &
echo "Scheduling Service started on port 8004 (PID: $!)"

# Start Workflow Orchestrator
cd ../workflow-orchestrator
PYTHONPATH=../.. nohup uvicorn main:app --host 0.0.0.0 --port 8005 > ../../logs/workflow-orchestrator.log 2>&1 &
echo "Workflow Orchestrator started on port 8005 (PID: $!)"

# Start API Gateway
cd ../api-gateway
PYTHONPATH=../.. nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../../logs/api-gateway.log 2>&1 &
echo "API Gateway started on port 8000 (PID: $!)"

cd ~/chatbot

echo ""
echo "✅ All services started!"
echo ""
echo "Check logs: tail -f logs/*.log"
echo "Check health: curl http://localhost:8000/health"
echo ""
echo "To stop all services, run: ./stop-services.sh"
