#!/bin/bash

# FinancePilot AI - Startup Script
# This script starts all required services

echo "Starting FinancePilot AI..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your GEMINI_API_KEY if desired"
    echo ""
fi

# Start ML Service
echo "Starting ML Service on port 8000..."
cd ml
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 &
ML_PID=$!
cd ..
echo "ML Service started (PID: $ML_PID)"
echo ""

# Wait for ML service to be ready
echo "Waiting for ML service to be ready..."
sleep 3

# Start Express Backend
echo "Starting Express Backend on port 3001..."
PORT=3001 ML_SERVICE_URL=http://localhost:8000 node server/index.cjs &
API_PID=$!
echo "Express Backend started (PID: $API_PID)"
echo ""

# Wait for API to be ready
echo "Waiting for API to be ready..."
sleep 2

# Start React Frontend
echo "Starting React Frontend on port 5173..."
npm run dev &
WEB_PID=$!
echo "React Frontend started (PID: $WEB_PID)"
echo ""

echo "=========================================="
echo "FinancePilot AI is now running!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "API: http://localhost:3001"
echo "ML Service: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $ML_PID 2>/dev/null
    kill $API_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    echo "All services stopped"
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
