#!/bin/bash
set -e

echo "Starting deploy..."
cd /home/ubuntu/website-wizard

echo "Pulling latest code..."
git fetch origin
git reset --hard origin/main

echo "Installing dependencies..."
npm ci

echo "Restarting service..."
sudo systemctl restart buddii-api

echo "Checking service status..."
sudo systemctl is-active buddii-api

echo "Deploy complete."
