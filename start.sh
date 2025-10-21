#!/bin/bash

echo "=========================================="
echo "AIcoin Trading System - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from env.example..."
    cp env.example .env
    echo "✅ .env file created"
    echo ""
    echo "📝 Please edit .env file and add your API keys:"
    echo "   - DEEPSEEK_API_KEY=your-key-here"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

echo "🚀 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T backend python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

echo ""
echo "=========================================="
echo "✅ AIcoin Trading System is running!"
echo "=========================================="
echo ""
echo "📊 Services:"
echo "   - Frontend:  http://localhost:3000"
echo "   - API Docs:  http://localhost:8000/docs"
echo "   - Backend:   http://localhost:8000"
echo ""
echo "🔍 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop system:"
echo "   docker-compose down"
echo ""
echo "Happy trading! 🚀"

