# Website Wizard Operations Guide

**Version:** v1.0.0

---

# Overview

This document describes the day-to-day operational procedures for Website Wizard.

It is intended for developers, system administrators, DevOps engineers, and support personnel responsible for maintaining the platform.

Topics include:

* Service management
* Health monitoring
* Routine maintenance
* Database operations
* Queue management
* Log inspection
* Performance monitoring
* Operational checklists

---

# Operational Architecture

Website Wizard consists of several independently managed services.

```text
Frontend
     │
     ▼
FastAPI Backend
     │
     ├────────► PostgreSQL
     │
     └────────► Redis
                     │
                     ▼
                 Celery Worker
                     │
                     ▼
                 OpenAI API

Monitoring

Prometheus
Grafana
Flower
```

---

# Daily Operational Checklist

At the beginning of each day verify:

* All Docker containers are running
* Backend is reachable
* Celery worker is processing tasks
* PostgreSQL is available
* Redis is available
* No excessive task backlog
* Disk space is sufficient
* Recent website generations completed successfully

---

# Service Management

## View Running Services

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

---

## Restart Backend

```bash
docker compose restart backend
```

---

## Restart Celery

```bash
docker compose restart celery
```

---

## Restart PostgreSQL

```bash
docker compose restart postgres
```

---

## Restart Redis

```bash
docker compose restart redis
```

---

## Restart Entire Stack

```bash
docker compose restart
```

---

# Health Checks

## Backend

Verify API availability.

Example:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## Celery

Verify:

* Worker running
* Tasks processing
* No excessive retries

Flower provides real-time worker visibility.

---

## PostgreSQL

Connect:

```bash
docker compose exec postgres \
psql -U ww_admin -d level6db
```

Simple verification:

```sql
SELECT NOW();
```

---

## Redis

Verify container status:

```bash
docker compose ps redis
```

Confirm Celery connectivity.

---

# Website Generation Verification

Generate a small test project.

Confirm:

* Generation completed
* HTML generated
* CSS generated
* JavaScript generated
* Metadata persisted
* autonomous_core exists

Recommended SQL:

```sql
SELECT
    project_name,
    generation_status,
    metadata_json IS NOT NULL
FROM generated_sites
ORDER BY created_at DESC
LIMIT 5;
```

---

# Monitoring

## Prometheus

Responsible for:

* Metrics collection
* Service monitoring
* Performance metrics

---

## Grafana

Provides dashboards for:

* System health
* Generation activity
* Resource utilization
* Performance trends

---

## Flower

Provides:

* Celery worker monitoring
* Active tasks
* Failed tasks
* Retry information
* Queue inspection

---

# Log Management

## View All Logs

```bash
docker compose logs
```

---

## Backend Logs

```bash
docker compose logs backend
```

---

## Celery Logs

```bash
docker compose logs celery
```

---

## PostgreSQL Logs

```bash
docker compose logs postgres
```

---

## Continuous Log Streaming

```bash
docker compose logs -f backend
```

---

# Database Operations

Useful queries include:

Completed projects:

```sql
SELECT
project_name,
generation_status
FROM generated_sites
WHERE generation_status='completed';
```

Recent generations:

```sql
SELECT
project_name,
created_at
FROM generated_sites
ORDER BY created_at DESC
LIMIT 10;
```

Projects missing metadata:

```sql
SELECT
COUNT(*)
FROM generated_sites
WHERE
generation_status='completed'
AND metadata_json IS NULL;
```

Historical records created before metadata persistence may legitimately appear in this query.

---

# Queue Operations

Celery should normally maintain a minimal queue.

Monitor:

* Queue length
* Retry count
* Failed jobs
* Processing time

Persistent queue growth may indicate:

* OpenAI latency
* Worker failure
* Redis issues
* Backend problems

---

# Performance Monitoring

Track:

* Generation duration
* GPT token usage
* Success rate
* Failure rate
* Queue depth
* Database growth

These metrics support capacity planning and troubleshooting.

---

# Routine Maintenance

Daily

* Verify services
* Review logs
* Confirm successful generations

Weekly

* Review resource usage
* Check disk utilization
* Validate backups

Monthly

* Update dependencies
* Review Docker images
* Archive logs if necessary
* Review monitoring dashboards

---

# Incident Response

If website generation fails:

1. Inspect backend logs.
2. Inspect Celery logs.
3. Verify Redis connectivity.
4. Verify PostgreSQL availability.
5. Verify OpenAI API connectivity.
6. Retry generation.
7. Document recurring failures.

---

# Operational Validation

Production validation confirmed:

* Backend restart recovery
* Celery restart recovery
* Full stack restart recovery
* Regression generation success
* Metadata persistence
* Autonomous pipeline persistence

These operational procedures were validated prior to the v1.0.0 release.

---

# Capacity Planning

As workload increases consider:

* Additional Celery workers
* Dedicated PostgreSQL server
* Dedicated Redis instance
* Reverse proxy
* Load balancing
* Increased storage
* Expanded monitoring

The architecture supports incremental scaling without redesign.

---

# Operational Best Practices

Recommended practices:

* Keep Docker images current
* Monitor logs daily
* Backup PostgreSQL regularly
* Test restore procedures
* Monitor queue health
* Review Grafana dashboards
* Keep documentation synchronized with releases

---

# Summary

The Website Wizard operational model is based on independently managed services supported by continuous monitoring, routine maintenance, and validated recovery procedures.

Following this guide helps ensure reliable website generation, consistent metadata persistence, and stable long-term operation in both development and production environments.
