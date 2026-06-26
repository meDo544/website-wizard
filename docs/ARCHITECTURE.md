# Website Wizard Architecture

**Version:** v1.0.0

---

# Overview

Website Wizard is an AI-powered website generation platform designed to transform a business description into a production-ready website.

The system combines:

* AI-powered website generation
* Background task processing
* Structured optimization metadata
* Autonomous learning architecture
* PostgreSQL persistence
* Docker-based deployment
* Monitoring and observability

The architecture emphasizes modularity, scalability, fault tolerance, and future extensibility.

---

# System Architecture

```text
                        User
                         │
                         ▼
                  Frontend Interface
                         │
                         ▼
                    FastAPI Backend
                         │
          Website Generation Request
                         │
                         ▼
                   Celery Task Queue
                         │
                         ▼
                AI Generation Engine
                         │
        HTML • CSS • JavaScript • Content
                         │
                         ▼
              Optimization & Scoring Engine
                         │
                         ▼
             Autonomous Metadata Pipeline
                         │
                         ▼
                  PostgreSQL Database
                         │
                         ▼
             Generated Website & Metadata
```

---

# Major Components

## Frontend

The frontend provides the user interface for creating websites.

Responsibilities:

* Collect business information
* Submit generation requests
* Display generation progress
* Present completed websites
* Allow regeneration when needed

---

## Backend API

The FastAPI backend coordinates all application logic.

Responsibilities:

* Validate incoming requests
* Authenticate users (where applicable)
* Queue generation jobs
* Retrieve completed projects
* Expose REST endpoints

The backend does not generate websites directly.

Instead, it delegates generation to background workers.

---

## Celery Worker

Website generation is performed asynchronously.

Responsibilities:

* Receive queued jobs
* Execute AI generation
* Build metadata pipeline
* Persist results
* Update generation status

Benefits:

* Improved scalability
* Better user experience
* Retry capability
* Worker isolation

---

## OpenAI Generation Engine

The generation engine transforms structured business information into a complete website.

Outputs include:

* HTML
* CSS
* JavaScript
* Business copy
* Calls to action
* Conversion-focused messaging

Generation statistics such as token usage and model information are recorded for operational monitoring.

---

## Optimization Engine

After content generation, Website Wizard evaluates the generated website.

Evaluation includes:

* Conversion score
* Quality score
* Overall score
* Variant tracking
* Industry profiling

These metrics provide the foundation for later optimization.

---

# Autonomous Metadata Pipeline

One of the defining architectural features of Website Wizard is the autonomous metadata pipeline.

Rather than storing only the generated website, the system stores structured metadata describing how the website was evaluated and processed.

The pipeline currently includes:

```text
performance_tracking
↓
conversion_prediction
↓
learning_profile
↓
optimization_recommendation
↓
variant_selection_strategy
↓
selection_override
↓
variant_application
↓
feedback_collection
↓
feedback_outcome
↓
learning_signal
↓
learning_accumulator
↓
adaptive_memory
↓
memory_consolidation
↓
optimization_knowledge
↓
knowledge_refinement
↓
optimization_intelligence
↓
autonomous_decision
↓
autonomous_action
↓
autonomous_execution
↓
autonomous_outcome
↓
autonomous_evaluation
↓
autonomous_adaptation
↓
autonomous_evolution
↓
autonomous_strategy
↓
autonomous_planning
↓
autonomous_coordination
↓
autonomous_orchestration
↓
autonomous_governance
↓
autonomous_self_improvement
↓
recursive_learning
↓
autonomous_core
```

Each stage records structured metadata within the project profile.

The current implementation establishes the architectural framework for future adaptive optimization without altering the generated website after completion.

---

# Database Layer

Website Wizard stores all generated projects inside PostgreSQL.

Each project contains:

* Generated HTML
* Generated CSS
* Generated JavaScript
* Generated URL
* GPT usage statistics
* Generation status
* Error information
* Structured metadata

The metadata is stored as JSON and contains the complete optimization pipeline.

---

# Runtime Services

The production environment is containerized using Docker Compose.

Primary services include:

* Backend API
* Celery Worker
* PostgreSQL
* Redis
* Prometheus
* Grafana
* Flower

Each service is independently restartable and supports operational monitoring.

---

# Request Lifecycle

A typical request follows these steps:

1. User submits website information.
2. Backend validates the request.
3. Backend creates a generation job.
4. Celery worker receives the task.
5. AI generates website assets.
6. Website quality and conversion metrics are calculated.
7. Metadata pipeline is assembled.
8. HTML, CSS, JavaScript, and metadata are persisted.
9. Project status is updated to `completed`.
10. Generated website becomes available to the user.

---

# Fault Tolerance

The architecture is designed to recover cleanly from common failures.

Validated recovery scenarios include:

* Backend restart
* Celery worker restart
* Simultaneous backend and worker restart

Production validation confirmed successful website generation following each recovery scenario.

---

# Scalability

The architecture supports future horizontal scaling through:

* Multiple Celery workers
* Separate database server
* Dedicated Redis instance
* Load-balanced API servers
* Independent monitoring services

The modular architecture enables new capabilities to be added without major redesign.

---

# Design Principles

Website Wizard follows several architectural principles:

* Separation of concerns
* Asynchronous processing
* Structured persistence
* Incremental extensibility
* Production validation
* Docker-first deployment
* Observability
* Maintainability

---

# Future Architecture

The current architecture establishes a stable foundation for future enhancements, including:

* Multi-page website generation
* Theme management
* AI image generation
* SEO optimization
* Analytics integration
* CMS export
* Plugin architecture
* Enterprise deployment options

These features can be added while preserving the existing architectural structure.

---

# Summary

Website Wizard v1.0.0 is a modular AI-powered website generation platform that combines asynchronous processing, structured optimization metadata, PostgreSQL persistence, and production-ready deployment.

The architecture separates generation, evaluation, persistence, and operations into independent components, enabling the platform to evolve while maintaining reliability, scalability, and maintainability.
