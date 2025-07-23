#!/bin/bash

echo "🚀 Starting RAG-based FAQ System (Simple Mode)..."

# Kill any existing processes
pkill -f uvicorn
pkill -f "npm run start"

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "🌐 Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend in background
echo "🎨 Starting React frontend..."
cd frontend && npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 Services started!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait 