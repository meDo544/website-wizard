# Website Wizard Database Design

**Version:** v1.0.0

---

# Overview

Website Wizard uses PostgreSQL as its primary relational database.

The database stores:

* User information
* Website generation requests
* Generated website assets
* AI generation statistics
* Project metadata
* Autonomous optimization pipeline
* Operational information

The database is designed to provide reliable persistence, structured querying, and future extensibility while maintaining compatibility with evolving metadata models.

---

# Database Technology

| Component            | Technology        |
| -------------------- | ----------------- |
| Database Engine      | PostgreSQL        |
| Data Model           | Relational + JSON |
| Primary Key Strategy | UUID              |
| Metadata Storage     | JSONB             |
| Background Access    | Celery Workers    |
| Application Access   | FastAPI Backend   |

---

# High-Level Data Model

```text
                 Users
                   │
                   │
          ┌────────▼────────┐
          │ generated_sites │
          └────────┬────────┘
                   │
                   │
           Generated Website
                   │
                   │
        HTML • CSS • JavaScript
                   │
                   │
             metadata_json
                   │
                   ▼
        Complete Metadata Pipeline
```

The `generated_sites` table is the primary persistence layer for website generation.

---

# Core Table: generated_sites

The `generated_sites` table stores both generated website assets and metadata.

Typical information includes:

* Project identifiers
* User association
* Business information
* Original prompt
* Generated HTML
* Generated CSS
* Generated JavaScript
* Generated URL
* GPT usage statistics
* Generation status
* Error information
* Metadata pipeline
* Creation timestamps

---

# Primary Columns

## Identity

| Column  | Description                      |
| ------- | -------------------------------- |
| id      | Unique project identifier (UUID) |
| user_id | Associated user identifier       |

---

## Project Information

| Column        | Description                 |
| ------------- | --------------------------- |
| project_name  | User-defined project name   |
| business_type | Business category           |
| prompt        | Original generation request |

---

## Generated Website

| Column        | Description                |
| ------------- | -------------------------- |
| html          | Generated HTML document    |
| css           | Generated stylesheet       |
| js            | Generated JavaScript       |
| generated_url | Published or generated URL |

---

## AI Generation Statistics

| Column                | Description            |
| --------------------- | ---------------------- |
| gpt_model             | AI model used          |
| gpt_tokens_prompt     | Prompt token count     |
| gpt_tokens_completion | Completion token count |
| gpt_tokens_total      | Total token usage      |

These fields support operational monitoring and cost analysis.

---

## Generation Status

| Column            | Description                              |
| ----------------- | ---------------------------------------- |
| generation_status | Current processing status                |
| error_message     | Generation error details (if applicable) |

Typical status values include:

* pending
* processing
* completed
* failed

---

## Metadata Storage

The metadata pipeline is stored inside:

```text
metadata_json
```

The primary object is:

```text
metadata_json
└── profile
```

This object contains the complete optimization and autonomous processing pipeline.

---

# Metadata Structure

Simplified representation:

```text
metadata_json
│
└── profile
    │
    ├── performance_tracking
    ├── conversion_prediction
    ├── learning_profile
    ├── optimization_recommendation
    ├── variant_selection_strategy
    ├── selection_override
    ├── variant_application
    ├── feedback_collection
    ├── feedback_outcome
    ├── learning_signal
    ├── learning_accumulator
    ├── adaptive_memory
    ├── memory_consolidation
    ├── optimization_knowledge
    ├── knowledge_refinement
    ├── optimization_intelligence
    ├── autonomous_decision
    ├── autonomous_action
    ├── autonomous_execution
    ├── autonomous_outcome
    ├── autonomous_evaluation
    ├── autonomous_adaptation
    ├── autonomous_evolution
    ├── autonomous_strategy
    ├── autonomous_planning
    ├── autonomous_coordination
    ├── autonomous_orchestration
    ├── autonomous_governance
    ├── autonomous_self_improvement
    ├── recursive_learning
    └── autonomous_core
```

Each stage is stored as an independent JSON object.

---

# Example Metadata

Example of the final pipeline stage:

```json
{
  "autonomous_core": {
    "core_strength": 0.0,
    "core_entries": 1,
    "core_status": "active",
    "core_source": "recursive_learning",
    "model_version": "v1"
  }
}
```

---

# Data Lifecycle

A project progresses through the following stages:

```text
Generation Request
        │
        ▼
Database Record Created
        │
        ▼
Queued for Processing
        │
        ▼
AI Website Generation
        │
        ▼
Metadata Pipeline Construction
        │
        ▼
Database Persistence
        │
        ▼
Generation Complete
```

At completion, both website assets and metadata are committed within the same project record.

---

# Data Integrity

The production validation process confirms:

* Successful website persistence
* Metadata persistence
* JSON structure validity
* Autonomous pipeline completeness
* Recovery after service restarts

Historical records created before metadata persistence may legitimately contain a `NULL` value for `metadata_json`.

---

# Query Examples

Retrieve completed projects:

```sql
SELECT
    project_name,
    generation_status
FROM generated_sites
WHERE generation_status = 'completed';
```

Retrieve autonomous core metadata:

```sql
SELECT
    project_name,
    metadata_json->'profile'->'autonomous_core'
FROM generated_sites;
```

Check for completed projects missing metadata:

```sql
SELECT
    COUNT(*)
FROM generated_sites
WHERE generation_status = 'completed'
  AND metadata_json IS NULL;
```

This query is useful for identifying historical pre-metadata records.

---

# Performance Considerations

Website Wizard uses PostgreSQL's relational storage for structured project information and JSON storage for flexible metadata.

Advantages include:

* Schema stability for core entities
* Flexible evolution of metadata
* Simplified migrations
* Backward compatibility
* Efficient querying of project information

As the metadata model evolves, new pipeline stages can be introduced without requiring disruptive schema changes.

---

# Backup Strategy

Recommended production practices include:

* Daily PostgreSQL backups
* Point-in-time recovery (where supported)
* Regular restore validation
* Off-site backup storage
* Backup monitoring

Operational recovery procedures are documented in `RECOVERY.md`.

---

# Future Database Evolution

Potential future enhancements include:

* Metadata indexing
* Partitioning for large datasets
* Read replicas
* Analytics tables
* Historical pipeline snapshots
* Data retention policies

These enhancements can be introduced while maintaining compatibility with the current schema.

---

# Summary

The Website Wizard database combines a relational PostgreSQL schema with structured JSON metadata to provide a flexible and extensible persistence layer.

Generated website assets, AI generation statistics, and the complete autonomous metadata pipeline are stored together, providing a comprehensive record of every website generation while supporting future expansion without major schema redesign.
