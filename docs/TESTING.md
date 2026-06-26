# TESTING.md

# Website Wizard Testing Guide

**Version:** v1.0.3

---

# Overview

Website Wizard includes an automated testing framework designed to verify the integrity of the application, database connectivity, metadata pipeline, and regression functionality.

The testing framework is based on **pytest** and provides repeatable validation of core platform functionality.

---

# Testing Objectives

The automated test suite verifies:

* Database connectivity
* Metadata generation integrity
* Autonomous Core metadata
* Regression stability

The goal is to detect regressions before deployment and maintain platform reliability.

---

# Testing Framework

Website Wizard uses:

* pytest
* python-dotenv
* psycopg2
* PostgreSQL

Development dependencies are maintained separately from production runtime dependencies.

---

# Test Directory Structure

```text
tests/
├── __init__.py
├── conftest.py
├── test_database_connection.py
├── test_metadata_integrity.py
├── test_autonomous_core.py
└── test_regression_suite.py
```

---

# Test Descriptions

## Database Connection

File:

```text
tests/test_database_connection.py
```

Purpose:

* Verify database connectivity
* Validate PostgreSQL configuration
* Confirm application credentials

---

## Metadata Integrity

File:

```text
tests/test_metadata_integrity.py
```

Purpose:

Validate generated metadata including:

* performance_tracking
* learning_profile
* adaptive_memory
* optimization_knowledge
* autonomous_core

---

## Autonomous Core

File:

```text
tests/test_autonomous_core.py
```

Purpose:

Verify Autonomous Core metadata.

Example fields:

* core_strength
* core_entries
* core_status
* core_source
* model_version

---

## Regression Suite

File:

```text
tests/test_regression_suite.py
```

Purpose:

Ensure previously implemented functionality continues to operate correctly after new releases.

Regression testing protects against accidental changes to the metadata pipeline and generation workflow.

---

# Running Tests

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run the complete test suite:

```bash
python -m pytest tests/ -q
```

Example successful output:

```text
......
6 passed in 0.26s
```

---

# Running Individual Tests

Database connectivity:

```bash
python -m pytest tests/test_database_connection.py -q
```

Metadata integrity:

```bash
python -m pytest tests/test_metadata_integrity.py -q
```

Autonomous Core:

```bash
python -m pytest tests/test_autonomous_core.py -q
```

Regression suite:

```bash
python -m pytest tests/test_regression_suite.py -q
```

---

# Development Environment

Activate the virtual environment before running tests:

```bash
source venv/bin/activate
```

Verify the interpreter:

```bash
python --version
```

If the virtual environment is not active, activate it before using `python`, `pip`, or `pytest`.

---

# Test Requirements

Development dependencies are maintained in:

```text
requirements-dev.txt
```

Runtime dependencies are maintained in:

```text
requirements.txt
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

---

# Regression Testing

Regression tests should be executed:

* Before every release
* After major feature additions
* After database schema changes
* Before merging significant changes

---

# Continuous Integration

Future CI/CD pipelines should automatically:

* Install dependencies
* Run the complete pytest suite
* Report test failures
* Block merges when tests fail

---

# Troubleshooting

## Database Authentication Errors

Verify:

* `.env` configuration
* `DATABASE_URL`
* PostgreSQL container status
* Virtual environment activation

---

## Missing Python Command

If `python` is not found:

```bash
source venv/bin/activate
```

---

## Missing Dependencies

Install development requirements:

```bash
pip install -r requirements-dev.txt
```

---

# Best Practices

* Run the full test suite before committing code.
* Keep tests independent and repeatable.
* Add tests alongside new features.
* Maintain separate runtime and development dependencies.
* Update regression tests whenever new functionality becomes part of the supported platform.

---

# Future Enhancements

Potential improvements include:

* GitHub Actions automated test execution
* Code coverage reporting
* Performance benchmarking
* API integration tests
* End-to-end generation tests
* Load and stress testing

---

# Summary

Website Wizard's automated testing framework provides repeatable verification of critical platform functionality. Combined with documentation, observability, and versioned releases, it helps ensure that changes can be introduced with confidence while reducing the risk of regressions.
