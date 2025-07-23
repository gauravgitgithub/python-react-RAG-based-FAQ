#!/bin/bash

# RAG-based FAQ System Startup Script

echo "🚀 Starting RAG-based FAQ System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Verify critical dependencies are installed
echo "🔍 Verifying critical dependencies..."
python3 -c "import fastapi, uvicorn, sqlalchemy, faiss, sentence_transformers, openai, cohere; print('✅ All critical dependencies installed')" || {
    echo "❌ Critical dependencies missing. Please check the installation."
    exit 1
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from template..."
    python3 setup_env.py
    echo "🔧 Please edit the .env file with your configuration before continuing."
    echo "💡 Run 'python3 setup_env.py help' for configuration guidance."
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm packages..."
    npm install
else
    echo "📦 npm packages already installed, checking for updates..."
    npm install
fi
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads models

# Set default environment variables if not set
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/rag_faq"
fi

if [ -z "$REDIS_URL" ]; then
    export REDIS_URL="redis://localhost:6379"
fi

if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="dev-secret-key-change-in-production"
fi

echo "✅ Environment setup complete!"
echo ""

# Kill any existing processes
echo "🔄 Stopping any existing processes..."
pkill -f uvicorn
pkill -f "npm start"
pkill -f "react-scripts"

# Start the backend server in background with increased timeout
echo "🌐 Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 --timeout-graceful-shutdown 300 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    echo "🔍 Checking for error logs..."
    ps aux | grep uvicorn
    exit 1
fi

# Start the frontend in background
echo "🎨 Starting React frontend..."
cd frontend
# Set port to 3001 for frontend and use --yes to automatically accept port changes
PORT=3001 npm start -- --yes &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 8

# Check if frontend is running on 3001
if curl -s http://localhost:3001/ > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3001"
elif curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 RAG-based FAQ System is now running!"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 ReDoc: http://localhost:8000/redoc"
echo "🌐 Frontend: http://localhost:3001 (or http://localhost:3000 if 3001 was busy)"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f uvicorn
    pkill -f "npm start"
    pkill -f "react-scripts"
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 