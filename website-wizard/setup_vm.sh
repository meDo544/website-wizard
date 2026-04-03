#!/bin/bash
set -e

echo "🚀 Setting up Docker + Compose v2..."

# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker + Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
echo "✅ Docker version:"
docker --version

echo "✅ Docker Compose version:"
docker compose version

# Cleanup old junk
echo "🧹 Cleaning old containers..."
docker system prune -af || true
docker volume prune -f || true

echo "✅ Setup complete"