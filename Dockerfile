# ---------------------------------------------------
# Base Image
# ---------------------------------------------------

FROM python:3.11-slim

# ---------------------------------------------------
# Environment Variables
# ---------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------------------------------------------
# Working Directory
# ---------------------------------------------------

WORKDIR /app

# ---------------------------------------------------
# System Dependencies (LEAN)
# ---------------------------------------------------

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# Python Dependencies
# ---------------------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------
# Copy Application
# ---------------------------------------------------

COPY . .

# ---------------------------------------------------
# Runtime Environment
# ---------------------------------------------------

ENV PYTHONPATH=/app

# ---------------------------------------------------
# Healthcheck
# ---------------------------------------------------

HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=20s \
            --retries=3 \
CMD curl --fail http://localhost:8000/health || exit 1

# ---------------------------------------------------
# Exposed Port
# ---------------------------------------------------

EXPOSE 8000

# ---------------------------------------------------
# Default Startup Command
# ---------------------------------------------------

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
