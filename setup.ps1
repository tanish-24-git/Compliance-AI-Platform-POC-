# Quick Setup Script for Compliance-First AI Platform (Windows)
# Run this in PowerShell

Write-Host "🛡️  Compliance-First AI Platform - Quick Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create it from .env.example" -ForegroundColor Red
    exit 1
}
Write-Host "✅ .env file found" -ForegroundColor Green

# Start Docker containers
Write-Host ""
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check backend health
Write-Host ""
Write-Host "🏥 Checking backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.Content -like '*"status":"healthy"*') {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend health check returned unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Backend health check failed. Check logs with: docker-compose logs backend" -ForegroundColor Yellow
}

# Seed database
Write-Host ""
Write-Host "🌱 Seeding database..." -ForegroundColor Yellow
docker exec -it compliance-backend python seed.py

# Setup frontend
Write-Host ""
Write-Host "📦 Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend
if (-Not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}
Set-Location ..

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 To start the application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Backend is already running at: http://localhost:8000" -ForegroundColor White
Write-Host "   - API docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   - Health check: http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host "   - Frontend will run at: http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access the database:" -ForegroundColor White
Write-Host "   docker exec -it compliance-postgres psql -U compliance -d compliance_db" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 See README.md for detailed usage instructions" -ForegroundColor Cyan
Write-Host "📊 See demo_queries.md for SQL queries to run during demos" -ForegroundColor Cyan
Write-Host ""
