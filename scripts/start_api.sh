#!/usr/bin/env bash

set -e

echo "========================================="
echo "🚀 Starting Website Wizard API"
echo "========================================="

# ---------------------------------------------------
# Environment Validation
# ---------------------------------------------------

if [ ! -f ".env" ]; then
  echo "❌ Missing .env file"
  exit 1
fi

# ---------------------------------------------------
# Run Database Migrations
# ---------------------------------------------------

echo "⏳ Running Alembic migrations..."

alembic upgrade head

echo "✅ Database migrations completed"

# ---------------------------------------------------
# Start FastAPI
# ---------------------------------------------------

echo "🚀 Launching FastAPI server..."

uvicorn backend.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
