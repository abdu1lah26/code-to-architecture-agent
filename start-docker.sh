#!/usr/bin/env bash

set -e

echo "🚀 Code-to-Architecture Agent - Docker Startup"
echo "=============================================="

# Make sure the script runs from the project root
cd "$(dirname "$0")"

# Load environment variables safely
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "❌ .env file not found"
  exit 1
fi

# Check required commands
if ! command -v docker > /dev/null 2>&1; then
  echo "❌ Docker is not installed or not available in PATH"
  exit 1
fi

if ! command -v curl > /dev/null 2>&1; then
  echo "❌ curl is not installed or not available in PATH"
  exit 1
fi

# Check if Ollama is running
echo "Checking Ollama connection..."

if ! curl -fsS http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "❌ Ollama is not running on http://localhost:11434"
  echo "Please start Ollama first:"
  echo "  ollama serve"
  exit 1
fi

echo "✅ Ollama is running"

# Build images
echo ""
echo "Building Docker images..."
docker compose build --no-cache

# Start services
echo ""
echo "Starting services..."
docker compose up -d

# Wait for PostgreSQL
echo ""
echo "Waiting for PostgreSQL..."

POSTGRES_READY=false

for i in {1..30}; do
  if docker exec code-to-arch-db \
    pg_isready -U "${DB_USER}" -d "${DB_NAME}" > /dev/null 2>&1; then
    POSTGRES_READY=true
    break
  fi

  sleep 2
done

if [ "$POSTGRES_READY" = true ]; then
  echo "✅ PostgreSQL is ready"
else
  echo "❌ PostgreSQL failed to become ready"
  docker compose logs postgres
  exit 1
fi

# Wait for Backend
echo ""
echo "Waiting for Backend..."

BACKEND_READY=false

for i in {1..30}; do
  if curl -fsS http://localhost:8000/health > /dev/null 2>&1; then
    BACKEND_READY=true
    break
  fi

  sleep 2
done

if [ "$BACKEND_READY" = true ]; then
  echo "✅ Backend is ready"
else
  echo "❌ Backend failed to become ready"
  docker compose logs backend
  exit 1
fi

# Wait for Frontend
echo ""
echo "Waiting for Frontend..."

FRONTEND_READY=false

for i in {1..30}; do
  if curl -fsS http://localhost:3000 > /dev/null 2>&1; then
    FRONTEND_READY=true
    break
  fi

  sleep 2
done

if [ "$FRONTEND_READY" = true ]; then
  echo "✅ Frontend is ready"
else
  echo "❌ Frontend failed to become ready"
  docker compose logs frontend
  exit 1
fi

echo ""
echo "=============================================="
echo "✅ All services started successfully!"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo ""
echo "View logs:"
echo "  docker compose logs -f"
echo ""
echo "Stop services:"
echo "  docker compose down"