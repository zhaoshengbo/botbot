#!/bin/bash

# BotBot Development Startup Script

echo "🦞 Starting BotBot Development Environment..."

# Check if .env files exist
if [ ! -f "be/.env" ]; then
    echo "⚠️  Backend .env not found. Copying from .env.example..."
    cp be/.env.example be/.env
    echo "✅ Created be/.env - Please edit with your configuration"
fi

if [ ! -f "fe/.env" ]; then
    echo "⚠️  Frontend .env not found. Copying from .env.example..."
    cp fe/.env.example fe/.env
    echo "✅ Created fe/.env"
fi

# Start Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "✨ BotBot is starting up!"
echo ""
echo "📍 Services:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo "   - MongoDB:   localhost:27017"
echo ""
echo "📋 Useful commands:"
echo "   - View logs:        docker-compose logs -f"
echo "   - Stop services:    docker-compose down"
echo "   - Restart:          docker-compose restart"
echo ""
echo "🔍 To view logs, run:"
echo "   docker-compose logs -f"
