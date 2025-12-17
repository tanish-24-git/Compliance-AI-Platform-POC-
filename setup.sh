#!/bin/bash

# Quick Setup Script for Compliance-First AI Platform
# This script automates the initial setup process

echo "🛡️  Compliance-First AI Platform - Quick Setup"
echo "=============================================="
echo ""

# Check if Docker is running
echo "📋 Checking prerequisites..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
echo "✅ Docker is running"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi
echo "✅ .env file found"

# Start Docker containers
echo ""
echo "🐳 Starting Docker containers..."
docker-compose up -d --build

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
echo ""
echo "🏥 Checking backend health..."
HEALTH_CHECK=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"')
if [ -z "$HEALTH_CHECK" ]; then
    echo "⚠️  Backend health check failed. Check logs with: docker-compose logs backend"
else
    echo "✅ Backend is healthy"
fi

# Seed database
echo ""
echo "🌱 Seeding database..."
docker exec -it compliance-backend python seed.py

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "🚀 To start the application:"
echo ""
echo "1. Backend is already running at: http://localhost:8000"
echo "   - API docs: http://localhost:8000/docs"
echo "   - Health check: http://localhost:8000/health"
echo ""
echo "2. Start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo "   - Frontend will run at: http://localhost:3000"
echo ""
echo "3. Access the database:"
echo "   docker exec -it compliance-postgres psql -U compliance -d compliance_db"
echo ""
echo "📚 See README.md for detailed usage instructions"
echo "📊 See demo_queries.md for SQL queries to run during demos"
echo ""
