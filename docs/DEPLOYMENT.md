# Website Wizard Deployment Guide

**Version:** v1.0.0

---

# Overview

This document describes how to deploy Website Wizard in both development and production environments.

Website Wizard is designed as a containerized application using Docker Compose, allowing consistent deployments across different operating systems and cloud providers.

The deployment architecture consists of multiple services working together to provide AI-powered website generation, background processing, database persistence, and operational monitoring.

---

# Deployment Architecture

```text
                    Internet
                        │
                        ▼
                 Reverse Proxy
                        │
                        ▼
                  FastAPI Backend
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
    Celery Worker                 PostgreSQL
         │
         ▼
       Redis
         │
         ▼
     OpenAI API

Monitoring Stack

Prometheus
Grafana
Flower
```

---

# System Requirements

## Minimum Requirements

| Component        | Requirement                            |
| ---------------- | -------------------------------------- |
| CPU              | 2 Cores                                |
| Memory           | 4 GB RAM                               |
| Storage          | 20 GB SSD                              |
| Operating System | Linux, macOS, Windows (Docker Desktop) |
| Docker           | Version 24+                            |
| Docker Compose   | Version 2+                             |

---

## Recommended Production

| Component     | Recommendation     |
| ------------- | ------------------ |
| CPU           | 4–8 Cores          |
| Memory        | 8–16 GB RAM        |
| Storage       | 100 GB SSD         |
| PostgreSQL    | Dedicated Volume   |
| Redis         | Dedicated Instance |
| Reverse Proxy | Nginx or Traefik   |
| TLS           | HTTPS Enabled      |

---

# Required Software

Install:

* Docker
* Docker Compose
* Git

Verify installation:

```bash
docker --version
docker compose version
git --version
```

---

# Clone the Repository

```bash
git clone <repository-url>
cd website-wizard
```

Replace `<repository-url>` with the actual Git repository URL.

---

# Environment Configuration

Create an environment file:

```text
.env
```

Typical variables include:

```text
OPENAI_API_KEY=
DATABASE_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
REDIS_URL=
SECRET_KEY=
```

Do **not** commit the `.env` file to version control.

---

# Docker Services

Website Wizard consists of the following services:

| Service    | Purpose                  |
| ---------- | ------------------------ |
| backend    | FastAPI application      |
| celery     | Background AI generation |
| postgres   | Primary database         |
| redis      | Message broker           |
| prometheus | Metrics collection       |
| grafana    | Monitoring dashboards    |
| flower     | Celery monitoring        |

---

# Starting the Application

Start all services:

```bash
docker compose up -d
```

Start with rebuild:

```bash
docker compose up --build -d
```

---

# Verify Running Containers

```bash
docker compose ps
```

Expected services:

* backend
* celery
* postgres
* redis
* prometheus
* grafana
* flower

All services should report a healthy or running state.

---

# Viewing Logs

All services:

```bash
docker compose logs
```

Specific service:

```bash
docker compose logs backend
```

Follow logs continuously:

```bash
docker compose logs -f backend
```

---

# Restarting Services

Restart backend:

```bash
docker compose restart backend
```

Restart Celery:

```bash
docker compose restart celery
```

Restart all services:

```bash
docker compose restart
```

These restart procedures were validated during production hardening.

---

# Stopping the Application

Stop services:

```bash
docker compose stop
```

Stop and remove containers:

```bash
docker compose down
```

Stop and remove containers with volumes:

```bash
docker compose down -v
```

**Warning:** Removing volumes deletes persistent database data.

---

# Database

The PostgreSQL database stores:

* Projects
* Generated websites
* Metadata pipeline
* AI generation statistics

Connect to PostgreSQL:

```bash
docker compose exec postgres psql -U ww_admin -d level6db
```

---

# Database Backups

Example backup:

```bash
docker compose exec postgres pg_dump \
-U ww_admin \
level6db \
> backup.sql
```

Restore:

```bash
psql level6db < backup.sql
```

Always verify backups by performing a restore test.

---

# Updating Website Wizard

Pull the latest code:

```bash
git pull origin main
```

Rebuild containers:

```bash
docker compose up --build -d
```

Verify:

```bash
docker compose ps
```

Run smoke tests before declaring the deployment successful.

---

# Health Verification

Verify:

* Backend responds
* Celery running
* Redis connected
* PostgreSQL reachable
* OpenAI connectivity
* Website generation succeeds

Recommended validation:

1. Generate a test website.
2. Confirm generation completes.
3. Verify metadata persistence.
4. Confirm `autonomous_core` exists.

---

# Production Deployment Recommendations

For production deployments:

* Enable HTTPS
* Use a reverse proxy
* Secure environment variables
* Restrict database access
* Enable automated backups
* Configure monitoring alerts
* Rotate secrets regularly

---

# Monitoring Services

Website Wizard includes:

Prometheus

* Metrics collection

Grafana

* Dashboards
* Performance visualization

Flower

* Celery task monitoring

These services should remain available in production.

---

# Troubleshooting

## Backend Fails to Start

Check:

```bash
docker compose logs backend
```

Verify:

* Environment variables
* Database connectivity
* OpenAI API key

---

## Celery Not Processing

Check:

```bash
docker compose logs celery
```

Verify:

* Redis connection
* Queue status
* Backend connectivity

---

## PostgreSQL Connection Errors

Verify:

* Database container running
* Credentials
* Docker networking

---

## OpenAI Errors

Verify:

* API key
* Network connectivity
* API quota
* Service availability

---

# Production Validation

Version **v1.0.0** successfully completed:

* End-to-end validation
* Database integrity validation
* Regression testing
* Performance benchmarking
* Backend restart recovery
* Celery restart recovery
* Full system restart recovery

These validation results provide confidence for production deployment.

---

# Future Deployment Enhancements

Planned improvements include:

* Kubernetes deployment
* High-availability PostgreSQL
* Horizontal Celery scaling
* Object storage integration
* Blue/green deployments
* Automated infrastructure provisioning
* CI/CD deployment automation

---

# Summary

Website Wizard is deployed as a Docker Compose application consisting of independently managed services for API processing, background task execution, database persistence, messaging, and monitoring.

The deployment architecture supports local development, production deployment, operational monitoring, and future horizontal scaling while maintaining a straightforward deployment workflow.
