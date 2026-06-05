#!/usr/bin/env bash

set -e

echo "========================================="
echo "🌸 Starting Flower Monitoring"
echo "========================================="

# ---------------------------------------------------
# Environment Validation
# ---------------------------------------------------

if [ ! -f ".env" ]; then
  echo "❌ Missing .env file"
  exit 1
fi

# ---------------------------------------------------
# Start Flower
# ---------------------------------------------------

echo "🚀 Launching Flower..."

celery \
    -A backend.core.celery_app.celery \
    flower \
    --port=5555
