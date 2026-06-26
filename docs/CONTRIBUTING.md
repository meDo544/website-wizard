# Contributing to Website Wizard

**Version:** v1.0.0

---

# Welcome

Thank you for your interest in contributing to Website Wizard.

Website Wizard is an AI-powered website generation platform designed with a strong emphasis on maintainability, reliability, and production readiness.

This document describes the recommended workflow, coding standards, testing expectations, and release practices for contributors.

Whether you are fixing a bug, improving documentation, or implementing a new feature, following these guidelines helps maintain the quality and stability of the project.

---

# Guiding Principles

Contributions should follow these principles:

* Keep changes focused.
* Prefer incremental improvements.
* Validate changes before committing.
* Document new functionality.
* Preserve backward compatibility whenever practical.
* Prioritize maintainability over complexity.

---

# Development Workflow

The recommended development workflow is:

```text id="8wh7zm"
Design
    ↓
Implement
    ↓
Compile
    ↓
Test
    ↓
Validate
    ↓
Document
    ↓
Commit
    ↓
Tag (when appropriate)
```

Every completed feature should be fully validated before being merged.

---

# Branch Strategy

Recommended branch structure:

```text id="0h7v2x"
main

feature/<feature-name>

bugfix/<issue-name>

release/<version>

hotfix/<version>
```

The `main` branch should always remain deployable.

---

# Local Development

Clone the repository:

```bash id="6g4n6z"
git clone <repository-url>
cd website-wizard
```

Start the development environment:

```bash id="o9mghl"
docker compose up -d
```

Verify services:

```bash id="y84otq"
docker compose ps
```

---

# Coding Standards

General recommendations:

* Write clear, readable code.
* Use descriptive variable names.
* Keep functions focused.
* Avoid unnecessary complexity.
* Follow existing project conventions.
* Add comments only where they improve understanding.

Consistency is preferred over personal coding style.

---

# Documentation Requirements

Every significant change should include corresponding documentation updates.

Examples:

* New API endpoint → update `API.md`
* Database change → update `DATABASE.md`
* Pipeline change → update `PIPELINE.md`
* Deployment change → update `DEPLOYMENT.md`

Documentation should evolve with the codebase.

---

# Testing Requirements

Before submitting changes:

Compile:

```bash id="a8bx3z"
python3 -m py_compile backend/services/gpt_website_generator.py
```

Run application tests.

Generate at least one website.

Verify:

* Successful generation
* Metadata persistence
* Database integrity

When applicable, add or update automated tests.

---

# Validation Checklist

Before creating a pull request:

* Code compiles successfully
* Tests pass
* Documentation updated
* No unintended changes
* Docker environment verified
* Database validation completed

Production-facing changes should include evidence of successful validation.

---

# Commit Messages

Use clear, descriptive commit messages.

Examples:

```text id="76ozwm"
Fix metadata persistence issue

Improve deployment documentation

Add autonomous evaluation stage

Refactor database validation

Update recovery procedures
```

Avoid vague commit messages such as:

```text id="vvb39v"
Fix stuff

Update code

Changes
```

---

# Versioning

Website Wizard follows Semantic Versioning.

```text id="2sp7kq"
MAJOR.MINOR.PATCH
```

Examples:

```text id="sm7h2t"
v1.0.1

Bug fixes

v1.1.0

New features

v2.0.0

Breaking architectural changes
```

---

# Pull Requests

Pull requests should include:

* Summary of changes
* Motivation
* Testing performed
* Documentation updates
* Known limitations (if any)

Small, focused pull requests are preferred over large changes.

---

# Issue Reporting

When reporting issues include:

* Environment
* Version
* Steps to reproduce
* Expected behavior
* Actual behavior
* Error messages
* Relevant logs

The more information provided, the easier it is to reproduce and resolve the issue.

---

# Feature Requests

Feature requests should describe:

* Problem being solved
* Proposed solution
* Benefits
* Possible alternatives
* Backward compatibility considerations

Discussion before implementation is encouraged.

---

# Release Process

Typical release workflow:

```text id="gtlq8k"
Implement
    ↓
Validate
    ↓
Update Documentation
    ↓
Commit
    ↓
Tag
    ↓
Push
    ↓
Release
```

Major releases should include release notes and validation summaries.

---

# Code Reviews

Reviewers should consider:

* Correctness
* Maintainability
* Security
* Performance
* Documentation
* Test coverage

Constructive feedback is encouraged.

---

# Project Philosophy

Website Wizard has been developed using an incremental engineering approach.

The project values:

* Reliable software
* Production validation
* Continuous improvement
* Clear documentation
* Sustainable architecture

Contributors are encouraged to preserve these principles.

---

# Community Standards

Please:

* Be respectful.
* Assume good intent.
* Provide constructive feedback.
* Encourage collaboration.
* Help improve documentation.

A welcoming and professional community benefits everyone.

---

# Recognition

Every contribution is valuable.

Contributions may include:

* Code
* Documentation
* Testing
* Bug reports
* Feature suggestions
* Performance improvements
* Operational improvements

Improving any part of the project helps strengthen the platform.

---

# Summary

Website Wizard is built through careful, incremental engineering.

By following the contribution guidelines in this document, contributors help ensure that new functionality is reliable, well-tested, documented, and consistent with the project's long-term goals.

The objective is not only to build new features, but to maintain a stable, production-quality platform that continues to evolve through disciplined software engineering.
