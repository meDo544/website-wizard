# Website Wizard Recovery Guide

**Version:** v1.0.0

---

# Overview

This document describes the recovery procedures for Website Wizard.

Its purpose is to minimize downtime, preserve generated websites and metadata, and restore normal system operation after failures.

The recovery strategy is based on:

* Service isolation
* Docker container recovery
* PostgreSQL persistence
* Queue recovery
* Validated restart procedures
* Backup and restore processes

Several recovery scenarios described in this guide were successfully validated during the Website Wizard v1.0.0 production hardening process.

---

# Recovery Objectives

Primary objectives:

* Restore website generation
* Preserve generated projects
* Preserve metadata integrity
* Minimize downtime
* Restore background processing
* Maintain database consistency

---

# Recovery Architecture

```text id="2l7bva"
        Docker Compose
              │
 ┌────────────┼────────────┐
 ▼            ▼            ▼
Backend     Celery      PostgreSQL
 │             │              │
 ▼             ▼              ▼
Redis       OpenAI      Persistent Storage
```

Each service can be recovered independently.

---

# Recovery Levels

| Level   | Description                  |
| ------- | ---------------------------- |
| Level 1 | Single service restart       |
| Level 2 | Multiple service restart     |
| Level 3 | Full application restart     |
| Level 4 | Database restore             |
| Level 5 | Complete environment rebuild |

---

# Level 1 Recovery

## Backend Recovery

Restart:

```bash id="d5ks3k"
docker compose restart backend
```

Verify:

* Backend starts successfully
* API responds
* Website generation succeeds

This recovery scenario was validated before the v1.0.0 release.

---

## Celery Recovery

Restart:

```bash id="o8cfke"
docker compose restart celery
```

Verify:

* Worker starts
* Queue processes normally
* New generation requests complete

Validated during production testing.

---

## Redis Recovery

Restart:

```bash id="tbjyx0"
docker compose restart redis
```

Verify:

* Celery reconnects
* Tasks continue processing

---

## PostgreSQL Recovery

Restart:

```bash id="gxrxmk"
docker compose restart postgres
```

Verify:

```sql id="xbbs5k"
SELECT NOW();
```

Confirm database availability before resuming website generation.

---

# Level 2 Recovery

Restart selected services.

Example:

```bash id="d6ax6h"
docker compose restart backend celery
```

Verification:

* Backend operational
* Celery operational
* Successful website generation
* Metadata persistence

This recovery scenario was validated successfully.

---

# Level 3 Recovery

Restart entire application.

```bash id="y5d3lw"
docker compose restart
```

Verify:

* All services running
* No failed containers
* Database reachable
* Queue operational
* Successful website generation

---

# Recovery Validation

Following any restart:

Generate a small validation project.

Confirm:

* Generation completed
* HTML persisted
* CSS persisted
* JavaScript persisted
* Metadata persisted
* autonomous_core exists

Example SQL:

```sql id="s43p94"
SELECT
project_name,
generation_status,
metadata_json IS NOT NULL
FROM generated_sites
ORDER BY created_at DESC
LIMIT 5;
```

---

# Database Recovery

## Backup

Create backup:

```bash id="5bmrvc"
docker compose exec postgres pg_dump \
-U ww_admin \
level6db \
> backup.sql
```

---

## Restore

Restore database:

```bash id="zw6ztm"
psql level6db < backup.sql
```

After restoration:

* Verify schema
* Verify generated projects
* Verify metadata
* Generate a new website

Restore validation is strongly recommended after every backup procedure.

---

# Container Recovery

If containers become corrupted:

Stop:

```bash id="az9emr"
docker compose down
```

Rebuild:

```bash id="4ncl0u"
docker compose up --build -d
```

Verify:

```bash id="lm5r1x"
docker compose ps
```

---

# Metadata Recovery

Metadata is stored within PostgreSQL.

Verification query:

```sql id="qqrjlwm"
SELECT
project_name,
metadata_json->'profile'->'autonomous_core'
FROM generated_sites;
```

Historical projects created before metadata persistence may legitimately contain NULL metadata.

No corrective action is required unless metadata loss affects newly generated projects.

---

# OpenAI Connectivity Recovery

If generation fails:

Verify:

* API key
* Internet connectivity
* API quota
* Service availability

After restoring connectivity:

Generate a validation website.

---

# Queue Recovery

Verify:

* Redis running
* Celery worker running
* No excessive retries
* Queue draining normally

Flower should show active workers.

---

# Disaster Recovery

If the entire environment fails:

1. Provision a new server.
2. Install Docker.
3. Clone the repository.
4. Restore the environment configuration.
5. Restore the PostgreSQL backup.
6. Start Docker Compose.
7. Verify all services.
8. Generate a validation website.

---

# Validated Recovery Scenarios

The following scenarios were successfully validated during Website Wizard v1.0.0 production hardening:

| Scenario                        | Result |
| ------------------------------- | ------ |
| Backend restart                 | PASS   |
| Celery restart                  | PASS   |
| Backend + Celery restart        | PASS   |
| Regression website generation   | PASS   |
| Metadata persistence            | PASS   |
| Autonomous pipeline persistence | PASS   |

These procedures were executed and confirmed prior to the production release.

---

# Recovery Checklist

After any recovery:

* Backend running
* Celery running
* PostgreSQL available
* Redis available
* Monitoring available
* Website generation successful
* Metadata persisted
* autonomous_core present
* No unexpected errors

---

# Recovery Time Objectives

Suggested operational targets:

| Recovery Event           | Target       |
| ------------------------ | ------------ |
| Backend restart          | < 2 minutes  |
| Celery restart           | < 2 minutes  |
| Full application restart | < 5 minutes  |
| Database restore         | < 30 minutes |
| Full environment rebuild | < 2 hours    |

These objectives should be reviewed as the platform evolves.

---

# Future Recovery Enhancements

Potential future improvements:

* Automated backups
* Automated restore validation
* Multi-region backups
* High availability PostgreSQL
* Redis replication
* Blue/green deployments
* Automated failover
* Infrastructure as Code recovery

---

# Summary

Website Wizard employs a layered recovery strategy based on independently recoverable services, persistent PostgreSQL storage, and Docker-based deployment.

The restart procedures documented in this guide were successfully validated during the v1.0.0 production hardening process, demonstrating reliable recovery of website generation, metadata persistence, and autonomous pipeline integrity.

Routine backup testing and operational validation should continue as part of ongoing maintenance to ensure long-term resilience.
