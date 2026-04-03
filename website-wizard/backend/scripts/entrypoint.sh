#!/bin/bash
set -e

echo "⏳ Waiting for Postgres..."
python backend/scripts/wait_for_db.py

echo "🔍 Verifying required environment variables..."

if [ -z "$DATABASE_URL" ]; then
  echo "❌ DATABASE_URL is not set"
  exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "⚠️ WARNING: OPENAI_API_KEY is not set (API may fail)"
fi

echo "🚀 Starting API..."
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000