#!/bin/bash

echo "Stopping all microservices..."

# Kill all uvicorn processes
pkill -f "uvicorn main:app"

echo "✅ All services stopped!"
