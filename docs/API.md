# Website Wizard API Reference

**Version:** v1.0.0

---

# Overview

Website Wizard exposes a RESTful API that enables clients to generate AI-powered websites, retrieve generated projects, monitor generation progress, and access project information.

The API is implemented using **FastAPI** and communicates using JSON over HTTP.

---

# API Principles

The Website Wizard API is designed around the following principles:

* RESTful resource design
* JSON request and response bodies
* Asynchronous website generation
* Consistent error handling
* Stateless communication
* Future backward compatibility

---

# Base URL

Example:

```text
http://localhost:8000/api
```

Production deployments should replace the hostname with the appropriate domain.

---

# Authentication

Authentication depends on the deployment configuration.

Possible authentication methods include:

* Session authentication
* API tokens
* JWT bearer tokens

If authentication is enabled, clients must include the appropriate credentials with each request.

Example:

```http
Authorization: Bearer <access_token>
```

---

# Content Type

Requests:

```http
Content-Type: application/json
```

Responses:

```http
Content-Type: application/json
```

---

# API Endpoints

---

# Generate Website

Creates a new AI website generation request.

## Endpoint

```http
POST /generate
```

---

## Request

Example:

```json
{
  "project_name": "Joe's Pizza",
  "business_type": "Restaurant",
  "prompt": "Create a modern pizza restaurant website with online ordering."
}
```

---

## Successful Response

```json
{
  "status": "accepted",
  "project_id": "uuid",
  "generation_status": "queued"
}
```

---

## Description

The backend validates the request and places the generation task onto the Celery queue.

Website generation occurs asynchronously.

---

# Get Project

Returns information about a generated project.

## Endpoint

```http
GET /projects/{project_id}
```

---

## Response

Example:

```json
{
  "project_id": "uuid",
  "project_name": "Joe's Pizza",
  "generation_status": "completed",
  "generated_url": "/generated/joes-pizza"
}
```

---

# List Projects

Returns all available projects.

## Endpoint

```http
GET /projects
```

---

## Response

Example:

```json
[
  {
    "project_name": "Joe's Pizza",
    "generation_status": "completed"
  },
  {
    "project_name": "Dental Clinic",
    "generation_status": "processing"
  }
]
```

---

# Check Generation Status

Returns the current processing status.

## Endpoint

```http
GET /status/{project_id}
```

---

## Response

```json
{
  "generation_status": "completed"
}
```

Possible status values include:

* pending
* queued
* processing
* completed
* failed

---

# Retrieve Generated Website

Returns the generated website assets.

## Endpoint

```http
GET /projects/{project_id}/website
```

---

## Response

Example:

```json
{
  "html": "...",
  "css": "...",
  "js": "..."
}
```

---

# Retrieve Metadata

Returns the stored metadata profile.

## Endpoint

```http
GET /projects/{project_id}/metadata
```

---

## Response

Example:

```json
{
  "profile": {
    "performance_tracking": {},
    "learning_profile": {},
    "autonomous_core": {}
  }
}
```

The complete metadata pipeline is documented in `PIPELINE.md`.

---

# Delete Project

Deletes a generated project.

## Endpoint

```http
DELETE /projects/{project_id}
```

---

## Response

```json
{
  "status": "deleted"
}
```

---

# Health Check

Returns service health information.

## Endpoint

```http
GET /health
```

---

## Example Response

```json
{
  "status": "healthy"
}
```

This endpoint is intended for monitoring systems and load balancers.

---

# Error Responses

The API returns standard HTTP status codes.

| Code | Meaning                         |
| ---- | ------------------------------- |
| 200  | Success                         |
| 201  | Resource created                |
| 202  | Request accepted for processing |
| 400  | Invalid request                 |
| 401  | Unauthorized                    |
| 403  | Forbidden                       |
| 404  | Resource not found              |
| 409  | Conflict                        |
| 422  | Validation error                |
| 500  | Internal server error           |
| 503  | Service unavailable             |

---

# Error Format

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Project name is required."
  }
}
```

Applications should rely on HTTP status codes and error codes rather than parsing message text.

---

# Generation Workflow

Website generation follows the sequence below:

```text
Client
   │
   ▼
POST /generate
   │
   ▼
FastAPI Validation
   │
   ▼
Celery Queue
   │
   ▼
AI Generation
   │
   ▼
Metadata Pipeline
   │
   ▼
PostgreSQL
   │
   ▼
GET /status
   │
   ▼
GET /projects/{id}
```

---

# Response Times

Typical request behavior:

| Operation      | Behavior                  |
| -------------- | ------------------------- |
| POST /generate | Immediate acknowledgement |
| AI generation  | Background processing     |
| GET requests   | Immediate response        |

Generation duration depends on AI response time and workload.

---

# Versioning Strategy

Future API versions should maintain backward compatibility whenever practical.

Recommended version format:

```text
/api/v1/
/api/v2/
```

Breaking changes should be introduced only through a new API version.

---

# Security Considerations

Recommended production practices include:

* HTTPS only
* Authentication
* Authorization
* Rate limiting
* Request validation
* Input sanitization
* Audit logging

Further guidance is provided in `SECURITY.md`.

---

# Future API Enhancements

Planned capabilities include:

* Multi-page website generation
* Project export
* Theme management
* AI image generation
* SEO analysis
* Analytics endpoints
* Batch generation
* Webhook notifications

These enhancements are expected to extend the existing API while maintaining compatibility with current clients.

---

# Summary

The Website Wizard API provides a clean REST interface for AI-powered website generation.

By separating request submission, asynchronous processing, project retrieval, and metadata access, the API supports scalable website generation while remaining simple for clients to integrate.

As the platform evolves, new endpoints and capabilities will be introduced without compromising the stability of the existing API.
