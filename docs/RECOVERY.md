# Website Wizard Recovery Guide

**Version:** v1.0.4

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

## Automated Local Backup

Website Wizard creates automated PostgreSQL custom-format backups using `/usr/local/sbin/website-wizard-backup.sh`.

The backup process:

* Uses `pg_dump -Fc --no-owner --no-acl`
* Validates the archive with `pg_restore`
* Generates a SHA-256 checksum
* Stores backups in `/var/backups/website-wizard`
* Restricts the backup directory and files to root access
* Applies approximately 14 days of local retention

The systemd backup timer runs daily at approximately **02:00 UTC**.

Production backup units:

* `website-wizard-backup.service`
* `website-wizard-backup.timer`

Automated backup creation must never automatically trigger restoration into the production database.

---

## Off-Site Backup Replication

Verified local backups are replicated to the private Google Cloud Storage bucket:

`gs://project-6d15b393-133a-40fd-aa9-ww-postgres-backups`

Cloud replication is performed by `/usr/local/sbin/website-wizard-cloud-backup.sh`.

The cloud replication timer runs daily at approximately **02:15 UTC**, after the local backup schedule.

Production cloud-backup units:

* `website-wizard-cloud-backup.service`
* `website-wizard-cloud-backup.timer`

The replication process verifies the local SHA-256 checksum before upload and uses create-only semantics so an existing backup object cannot be silently overwritten.

Backup objects are organized under `postgres/YYYY/MM/DD/`.

The GCS lifecycle policy removes live objects at 30 or more days since creation. GCS Soft Delete is enabled for 7 days, so recoverability may extend beyond removal from the live object namespace.

---

## Backup Security Model

Backup creation and disaster recovery use separate service identities.

Backup uploader:

`website-wizard-backup@project-6d15b393-133a-40fd-aa9.iam.gserviceaccount.com`

The backup uploader has create-only object permission on the backup bucket.

Recovery reader:

`website-wizard-recovery@project-6d15b393-133a-40fd-aa9.iam.gserviceaccount.com`

The recovery reader has read-only object access to the backup bucket.

Recovery access uses short-lived service-account impersonation. Long-lived JSON service-account keys must not be created or distributed for this recovery process.

The production VM should not be granted backup-bucket read access merely to simplify recovery. Backup retrieval remains a separate operator-controlled operation.

---

## Restore and Integrity Validation

Every database archive has a companion `.sha256` file.

Before restoration:

1. Confirm the archive and checksum file exist.
2. Calculate the archive SHA-256 digest.
3. Confirm it matches the stored digest.
4. Confirm `pg_restore` can read the custom-format archive.

Example archive check:

`pg_restore --list level6db_YYYYMMDD_HHMMSS.dump >/dev/null`

A backup that fails checksum or archive validation must not be restored.

## Isolated Restore Validation

Restore a backup into an isolated PostgreSQL 16 environment before considering a production restore.

The validation environment must use:

* A separate PostgreSQL container
* A separate Docker volume
* A separate database name
* No production database volume
* No production host port
* Test-only credentials

Use `pg_restore` with `--no-owner`, `--no-acl`, and `--exit-on-error`.

After restoration, validate at minimum:

* PostgreSQL connectivity
* Expected public-table count
* Alembic migration revision
* Critical table row counts
* Metadata availability
* Archive integrity

## Production Restore Guardrail

Do not restore directly over the running production database as a routine backup test.

A production restore is an operator-controlled disaster-recovery action. Before modifying production data:

1. Confirm that a genuine recovery condition exists.
2. Identify the exact backup and timestamp.
3. Verify its SHA-256 checksum.
4. Successfully restore and validate it in isolation.
5. Confirm the production database and volume being targeted.
6. Stop application writers before modifying production data.
7. Preserve the current production database or volume when technically possible.
8. Perform the controlled restore.
9. Validate schema, migration revision, critical data, application health, and website generation before normal traffic resumes.

Never use an automated timer or unattended process to overwrite the production database.

---

## Validated Recovery Evidence

The database disaster-recovery path was successfully exercised on **2026-09-30**.

Validated recovery chain:

`Production PostgreSQL -> automated pg_dump -> custom-format archive + SHA-256 -> create-only GCS replication -> read-only recovery identity -> keyless download -> SHA-256 verification -> isolated PostgreSQL 16 restore -> data validation`

Validated backup:

* Archive: `level6db_20260930_020001.dump`
* SHA-256: `6e8de61466c18d50ea970081675e86861ff75428ae59b4d74c552566f5ee84ab`
* Public tables: 15
* Alembic revision: `add_generation_fence`
* `generated_sites` rows: 296
* `users` rows: 2

The cloud-retrieved archive was byte-identical to the verified source backup and restored successfully into an isolated PostgreSQL 16 environment without modifying the production database or production volume.

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

If the production environment suffers a major or complete failure, recovery must proceed as a controlled operation.

## Recovery Sequence

1. Confirm the scope of the production failure.
2. Provision or recover the required compute environment.
3. Install Docker and required host dependencies.
4. Clone the Website Wizard repository at the intended recovery revision.
5. Restore protected environment configuration and required secrets through the approved operational process.
6. Identify the exact PostgreSQL backup to recover.
7. Retrieve the archive and companion SHA-256 checksum from the protected backup location.
8. Verify the SHA-256 digest before using the archive.
9. Confirm the custom-format archive is readable with `pg_restore`.
10. Restore the archive into an isolated PostgreSQL 16 environment first.
11. Validate schema, Alembic revision, critical row counts, and required metadata.
12. Only after isolated validation, perform an operator-controlled production database restore if required.
13. Start the Website Wizard Docker Compose services.
14. Verify PostgreSQL, Redis, backend, Celery, Flower, Prometheus, and Grafana.
15. Verify the backend health endpoint.
16. Generate a validation website and confirm expected application behavior before normal traffic resumes.

## Cloud Backup Retrieval

Off-site recovery uses the dedicated read-only recovery identity:

`website-wizard-recovery@project-6d15b393-133a-40fd-aa9.iam.gserviceaccount.com`

Use short-lived service-account impersonation to retrieve the selected archive and checksum from:

`gs://project-6d15b393-133a-40fd-aa9-ww-postgres-backups`

Do not create long-lived JSON service-account keys for disaster recovery.

The recovery identity must remain read-only. Recovery operations must not weaken the create-only permissions of the production backup uploader.

## Production Protection

Disaster-recovery testing must not modify:

* The running production PostgreSQL database
* The production Docker volume `website-wizard_postgres-data`
* Production backup objects
* Production service-account privilege boundaries

Routine restore validation must use isolated containers, volumes, database names, and test credentials.

A production restore requires deliberate operator approval after backup identity, checksum integrity, and isolated restore validation have all been confirmed.

---

# Validated Recovery Scenarios

The following recovery scenarios have been successfully validated.

| Scenario | Result |
| --- | --- |
| Backend restart | PASS |
| Celery restart | PASS |
| Backend + Celery restart | PASS |
| Regression website generation | PASS |
| Metadata persistence | PASS |
| Autonomous pipeline persistence | PASS |
| Unattended local PostgreSQL backup | PASS |
| SHA-256 backup integrity verification | PASS |
| Automated off-site GCS replication | PASS |
| Local isolated PostgreSQL 16 restore | PASS |
| Production/restored table-count comparison | PASS |
| Alembic revision comparison | PASS |
| Critical row-count comparison | PASS |
| Keyless recovery-identity impersonation | PASS |
| Read-only GCS archive and checksum retrieval | PASS |
| Cloud archive SHA-256 verification | PASS |
| Cloud-origin isolated PostgreSQL 16 restore | PASS |
| Recovery-test resource cleanup | PASS |
| Production health after recovery testing | PASS |

The original service-recovery scenarios were validated during Website Wizard v1.0.0 production hardening.

The backup and disaster-recovery scenarios were validated on **2026-09-30**. The recovery tests used isolated resources and did not modify the production PostgreSQL database or the production volume.

---

# Recovery Checklist

For database or disaster recovery, confirm the recovery source before modifying production:

* Exact backup archive and timestamp identified
* Companion SHA-256 checksum available
* Archive digest matches the stored checksum
* Custom-format archive is readable by `pg_restore`
* Recovery access uses the dedicated read-only recovery identity
* No long-lived JSON service-account key is required
* Backup has passed an isolated PostgreSQL 16 restore
* Expected public-table count verified
* Alembic migration revision verified
* Critical row counts verified
* Production database and target volume explicitly confirmed
* Production writers stopped before any production database modification
* Existing production data preserved where technically possible

After recovery, confirm:

* PostgreSQL available
* Redis available
* Backend running and healthy
* Celery running and healthy
* Flower running and healthy
* Prometheus available
* Grafana available
* Website generation successful
* Metadata persisted
* `autonomous_core` present where expected
* No unexpected application or service errors
* Temporary recovery containers, volumes, and downloaded archives cleaned up when no longer required

A recovery is not complete until both data integrity and application-level validation have succeeded.

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

The production backup and off-site replication system is operational, and isolated restore validation has been successfully demonstrated.

Potential future improvements include:

* Scheduled recurring non-production restore drills
* Point-in-time recovery (PITR)
* Multi-region backup replication
* High-availability PostgreSQL
* Redis replication
* Blue/green deployments
* Automated failover
* Infrastructure as Code recovery

Any future automation of restore testing must remain isolated from the production database and production volume.

---

# Summary

Website Wizard employs a layered recovery strategy based on independently recoverable services, persistent PostgreSQL storage, and Docker-based deployment.

The restart procedures documented in this guide were successfully validated during the v1.0.0 production hardening process, demonstrating reliable recovery of website generation, metadata persistence, and autonomous pipeline integrity.

Routine backup testing and operational validation should continue as part of ongoing maintenance to ensure long-term resilience.
