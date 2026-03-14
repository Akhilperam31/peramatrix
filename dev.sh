#!/bin/bash

# Peramatrix Development Startup Script
# This script runs both the FastAPI backend and the React dev server.

echo "🚀 Starting Peramatrix Development Environment..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT

# 1. Start Backend (Port 5000)
echo "Starting Backend on http://localhost:5000..."
python run.py &

# 2. Start Frontend (Port 3000)
echo "Starting Frontend on http://localhost:3000..."
cd frontend && npm start &

# Wait for background processes
wait
