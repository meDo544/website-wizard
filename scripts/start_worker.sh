#!/usr/bin/env bash

set -e

echo "========================================="
echo "⚙️ Starting Celery Worker"
echo "========================================="

# ---------------------------------------------------
# Environment Validation
# ---------------------------------------------------

if [ ! -f ".env" ]; then
  echo "❌ Missing .env file"
  exit 1
fi

# ---------------------------------------------------
# Start Celery Worker
# ---------------------------------------------------

echo "🚀 Launching Celery worker..."

celery \
    -A backend.core.celery_app.celery \
    worker \
    --loglevel=info
