# Changelog

All notable changes to Website Wizard are documented in this file.

The project follows the principles of **Semantic Versioning (SemVer)**.

Version format:

```text
MAJOR.MINOR.PATCH
```

---

# [v1.1.0] — Unreleased

**Development Status:** In Progress

## Phase 1 — Generation Intelligence & Self-Evaluation

### Added

* Added a structured generation evaluation framework with deterministic scoring and pass/improve/fail decisions.
* Added content and structural quality evaluation.
* Added business and industry alignment evaluation.
* Added conversion-readiness evaluation and hardened conversion-text validation.
* Added SEO readiness evaluation.
* Added accessibility readiness evaluation without representing the result as WCAG compliance.
* Added a bounded autonomous improvement loop with deterministic one-pass correction and reevaluation.
* Added a generation quality gate with pass, review, and fail decisions and explicit release-readiness metadata.
* Added generation-intelligence Prometheus metrics for quality-gate decisions, readiness scores, improvement outcomes, and pipeline duration.
* Added process-safe Prometheus multiprocess aggregation across the FastAPI backend and Celery workers.
* Added persistence of generation evaluation, SEO readiness, accessibility readiness, improvement, and quality-gate metadata within the generated website profile.

### Changed

* Improved atomic generated-site publication by removing the redundant nested generated-sites bind mount that crossed a filesystem mount boundary.
* Added shared Prometheus multiprocess storage for backend and Celery metric aggregation.
* Enabled centralized Celery lifecycle metric instrumentation and worker-process cleanup for live gauges.

### Validation

* Generation Intelligence & Self-Evaluation Phase 1 completed production validation.
* Production generation completed successfully through the authenticated API and Celery worker path.
* Persisted production readiness scores were Generation 94, SEO 83, and Accessibility 100.
* Production quality gate returned pass with release_ready=true and no blocking dimensions.
* Generated intelligence metadata persisted successfully in PostgreSQL under metadata_json.profile.
* Generated website publication completed atomically with no staging residue.
* Published website returned HTTP 200 and matched the persisted generated artifact.
* Prometheus successfully observed Celery-generated intelligence metrics through the backend scrape endpoint.
* Backend and Celery remained healthy after production validation.

### Impact

Website Wizard can now evaluate each generated website, identify improvement opportunities, apply bounded deterministic corrections when required, make an explicit quality-gate decision, persist the intelligence results, and expose production metrics for the complete evaluation path.

Phase 1 establishes the measurable self-evaluation foundation required for subsequent autonomous website-building capabilities.

---

# [v1.0.4] — CI/CD Automation

**Release Date:** June 2026

---

## Highlights

* Introduced GitHub Actions Continuous Integration workflow.
* Added automated Python source compilation.
* Added CI-safe unit testing with `pytest`.
* Refactored tests using a shared `conftest.py` fixture.
* Separated unit and integration tests using `pytest` markers.
* Added Docker Compose configuration validation.
* Added pip dependency caching for faster CI execution.

---

## Validation

* Unit Tests: 1 passed
* Integration Tests: 5 passed
* Full Test Suite: 6 passed
* GitHub Actions workflow executed successfully on GitHub-hosted runners.

---

## Impact

Completed the Continuous Integration foundation for Website Wizard.

---

# [v1.0.3] — Observability

**Release Date:** June 2026

---

## Highlights

* Added Prometheus metrics.
* Added Grafana dashboards.
* Added health and readiness endpoints.
* Added alerting rules.
* Introduced `OBSERVABILITY.md` documentation.

---

## Impact

Improved operational monitoring and production visibility.

---

# [v1.0.2] — Automated Testing

**Release Date:** June 2026

---

## Highlights

* Introduced automated testing using `pytest`.
* Added database connectivity tests.
* Added metadata integrity validation.
* Added Autonomous Core validation.
* Added regression test suite.

---

## Impact

Established repeatable automated validation for the platform.

---

# [v1.0.1] — Documentation Foundation

**Release Date:** June 2026

---

## Highlights

* Created comprehensive project documentation.
* Added architecture documentation.
* Added deployment, operations, recovery, and security guides.
* Added API and database documentation.
* Added contribution guidelines and release documentation.

---

## Impact

Established the documentation baseline for future development.

---

# [v1.0.0] — Production Release

**Release Date:** June 2026

## Overview

Website Wizard reached its first production-ready release after extensive implementation, validation, regression testing, recovery testing, and documentation.

This release establishes a stable foundation for future maintenance and feature development.

---

## Highlights

* Production-ready AI website generation
* Asynchronous generation using Celery
* PostgreSQL persistence
* Structured metadata pipeline
* Autonomous processing architecture
* Docker-based deployment
* Production validation
* Recovery validation
* Complete documentation suite

---

## Added

### AI Website Generation

* HTML generation
* CSS generation
* JavaScript generation
* Business-specific content generation
* Conversion-focused website creation

---

### Metadata Pipeline

Introduced structured metadata persistence including:

* Performance Tracking
* Conversion Prediction
* Learning Profile
* Optimization Recommendation
* Variant Selection Strategy
* Selection Override
* Variant Application
* Feedback Collection
* Feedback Outcome
* Learning Signal
* Learning Accumulator
* Adaptive Memory
* Memory Consolidation
* Optimization Knowledge
* Knowledge Refinement
* Optimization Intelligence
* Autonomous Decision
* Autonomous Action
* Autonomous Execution
* Autonomous Outcome
* Autonomous Evaluation
* Autonomous Adaptation
* Autonomous Evolution
* Autonomous Strategy
* Autonomous Planning
* Autonomous Coordination
* Autonomous Orchestration
* Autonomous Governance
* Autonomous Self-Improvement
* Recursive Learning
* Autonomous Core

---

### Infrastructure

* FastAPI backend
* Celery background processing
* Redis queue
* PostgreSQL database
* Docker Compose deployment
* Prometheus monitoring
* Grafana dashboards
* Flower task monitoring

---

### Documentation

Added:

* README.md
* ARCHITECTURE.md
* PIPELINE.md
* DATABASE.md
* API.md
* DEPLOYMENT.md
* OPERATIONS.md
* RECOVERY.md
* SECURITY.md
* CONTRIBUTING.md

---

## Validation

Completed:

* End-to-end testing
* Regression testing
* Database validation
* Metadata validation
* Recovery testing
* Production verification

Validated recovery scenarios:

* Backend restart
* Celery restart
* Backend + Celery restart

All validation scenarios completed successfully.

---

## Known Limitations

Historical projects created before metadata persistence may contain:

```text
metadata_json = NULL
```

These records remain valid historical data and do not affect new generations.

---

## Upgrade Notes

No upgrade actions are required for new installations.

Existing deployments should:

* Pull the latest source
* Rebuild Docker containers
* Verify environment variables
* Run a validation generation
* Confirm metadata persistence

---

# [v0.7.4]

## Added

* Autonomous Core
* Final autonomous processing stage
* Production validation prior to v1.0.0

---

# [v0.7.3]

## Added

* Recursive Learning

---

# [v0.7.2]

## Added

* Autonomous Self-Improvement

---

# [v0.7.1]

## Added

* Autonomous Governance

---

# [v0.7.0]

## Added

* Autonomous Orchestration

---

# [v0.6.9]

## Added

* Autonomous Coordination

---

# [v0.6.8]

## Added

* Autonomous Planning

---

# [v0.6.7]

## Added

* Autonomous Strategy

---

# [v0.6.6]

## Added

* Autonomous Evolution

---

# [v0.6.5]

## Added

* Autonomous Adaptation

---

# [v0.6.4]

## Added

* Autonomous Evaluation

---

# [v0.6.3]

## Added

* Autonomous Outcome

---

# [v0.6.2]

## Added

* Autonomous Execution

---

# [v0.6.1]

## Added

* Autonomous Action

---

# [v0.6.0]

## Added

* Autonomous Decision

---

# [Earlier Development]

The initial development phases established the core Website Wizard platform, including:

* FastAPI backend
* OpenAI integration
* HTML/CSS/JavaScript generation
* Celery background processing
* Redis integration
* PostgreSQL persistence
* Conversion scoring
* Learning profile generation
* Optimization pipeline
* Docker deployment
* Monitoring infrastructure

These foundational capabilities enabled the autonomous pipeline introduced throughout the v0.6.x and v0.7.x release series.

---

# Future Releases

## v1.1.x

Planned focus:

- Enhanced AI website generation
- Multi-page website generation
- Improved templates
- SEO enhancements
- Theme management
- Analytics integration
- Export capabilities
- Performance optimization

---

## v1.1

Planned features:

* Multi-page website generation
* SEO enhancements
* Theme management
* Analytics integration
* Export capabilities
* Expanded template library

---

## Changelog Guidelines

When updating this file:

* Record all user-visible changes.
* Group entries by version.
* Use clear categories such as **Added**, **Changed**, **Fixed**, **Removed**, and **Deprecated**.
* Keep entries concise and factual.
* Reference release notes for detailed explanations where appropriate.

---

# Summary

Website Wizard evolved from an AI-powered website generator into a production-ready platform through incremental engineering, continuous validation, and disciplined release management.

Version v1.0.4 completes the engineering foundation of Website Wizard by adding documentation, automated testing, observability, and Continuous Integration. Future development will focus primarily on expanding customer-facing capabilities while building upon this stable engineering platform.

