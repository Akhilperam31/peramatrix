#!/bin/bash

# Peramatrix Unified Production Startup Script
# This script launches the unified backend and HR service.

echo "🚀 Starting Peramatrix Unified Production Environment..."

# 1. Start Main Portal (Port 5000)
echo "Starting Main Portal on http://0.0.0.0:5000..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker run:socket_app --bind 0.0.0.0:5000 --daemon --access-logfile main_access.log --error-logfile main_error.log

# 2. Start HR Service (Port 8001)
echo "Starting HR Service on http://0.0.0.0:8001..."
gunicorn -w 2 -k uvicorn.workers.UvicornWorker run_hr:app --bind 0.0.0.0:8001 --daemon --access-logfile hr_access.log --error-logfile hr_error.log

echo "✅ Both services are running in the background."
echo "   Main Portal: http://localhost:5000"
echo "   HR Service:  http://localhost:8001"
echo ""
echo "Use 'ps aux | grep gunicorn' to check status or 'killall gunicorn' to stop."
