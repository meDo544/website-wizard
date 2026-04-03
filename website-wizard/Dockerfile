FROM python:3.11-slim

WORKDIR /app

# ---------------------------------------------------
# ENV (important for debugging + logs)
# ---------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------------------------------------------
# System dependencies
# ---------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    chromium \
    chromium-driver \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    wget \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# Node + Lighthouse
# ---------------------------------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g lighthouse \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# Install Python deps FIRST (better caching)
# ---------------------------------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------
# Copy app AFTER deps (important for rebuild correctness)
# ---------------------------------------------------
COPY . /app

# ---------------------------------------------------
# Ensure entrypoint is executable
# ---------------------------------------------------
RUN chmod +x /app/backend/scripts/entrypoint.sh

# ---------------------------------------------------
# DEBUG: show what code is actually inside container
# ---------------------------------------------------
RUN echo "===== DEBUG: auth.py inside container =====" \
    && cat /app/backend/routes/auth.py || true

# ---------------------------------------------------
# Expose port
# ---------------------------------------------------
EXPOSE 8000

# ---------------------------------------------------
# Start app
# ---------------------------------------------------
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]