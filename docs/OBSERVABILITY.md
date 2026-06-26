# OBSERVABILITY.md

# Website Wizard Observability Guide

**Version:** v1.0.3

---

# Overview

Website Wizard includes a production-ready observability stack designed to provide visibility into application health, performance, reliability, and operational behavior.

The observability platform consists of:

* FastAPI health endpoints
* Prometheus metrics
* Grafana dashboards
* Alert rules
* Structured logging
* Celery task instrumentation

Together, these components enable proactive monitoring and rapid troubleshooting.

---

# Observability Architecture

```
                    Website Wizard

                           │
                           ▼

                  FastAPI Application

                           │

        ┌──────────┬────────────┬───────────┐
        ▼          ▼            ▼
    /health     /ready      /metrics

                                  │
                                  ▼

                           Prometheus

                                  │
                                  ▼

                             Grafana

                                  │
                                  ▼

                              Operators
```

---

# Health Endpoints

## Health Check

Endpoint:

```
GET /health
```

Purpose:

Provides a lightweight indication that the application process is running.

Example:

```json
{
  "status": "ok"
}
```

---

## Readiness Check

Endpoint:

```
GET /ready
```

Purpose:

Indicates that the application is ready to receive requests.

Example:

```json
{
  "status": "ready"
}
```

---

# Prometheus Metrics

Endpoint:

```
GET /metrics
```

The metrics endpoint exports application and runtime metrics in Prometheus exposition format.

Metrics include both built-in Python metrics and Website Wizard application metrics.

---

# Metrics Categories

## HTTP

Examples:

* HTTP request count
* Request duration
* Active requests
* Error responses

---

## GPT

Examples:

* GPT request count
* GPT latency
* Token usage
* Cost metrics

---

## Lighthouse

Examples:

* Lighthouse execution count
* Lighthouse duration
* Timeout statistics

---

## Audit Pipeline

Examples:

* Audit throughput
* Audit duration
* Active audits
* Failed audits
* Retry counts

---

## Celery

Examples:

* Task execution count
* Task duration
* Retry count
* Failed tasks
* Active workers

---

## Python Runtime

Automatically exported metrics include:

* Garbage collection
* Memory usage
* CPU usage
* Process uptime
* File descriptors

---

# Prometheus Configuration

Location:

```
observability/prometheus/prometheus.yml
```

Current configuration includes:

* 15-second scrape interval
* 15-second evaluation interval
* Backend metrics scraping
* Prometheus self-monitoring

---

# Alert Rules

Location:

```
observability/prometheus/alerts.yml
```

Current alerts include:

## API

* High error rate
* High latency

---

## GPT

* GPT failure spike

---

## Lighthouse

* Timeout spike

---

## Celery

* Task failure rate

---

## Audit Pipeline

* Failure spike
* Audit saturation

Alerts are evaluated continuously by Prometheus.

---

# Grafana

Dashboard:

```
Website Wizard Overview
```

Location:

```
observability/grafana/dashboards/
```

Dashboard panels include:

* HTTP Request Rate
* HTTP Error Rate
* Active HTTP Requests
* GPT Request Rate
* GPT Token Usage
* Lighthouse p95 Duration
* Audit Throughput
* Active Audits
* Celery Task Failures

Grafana provisioning is automatic using the supplied datasource and dashboard configuration.

---

# Operational Validation

Health endpoint:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

Readiness endpoint:

```bash
curl http://localhost:8000/ready
```

Expected:

```json
{
  "status": "ready"
}
```

---

Metrics endpoint:

```bash
curl http://localhost:8000/metrics
```

Expected:

Prometheus metrics output containing application and runtime metrics.

---

# Troubleshooting

## Metrics unavailable

Verify:

* Backend container is running
* Prometheus is scraping the backend
* `/metrics` returns data

---

## Dashboard empty

Verify:

* Grafana datasource
* Prometheus target status
* Dashboard provisioning

---

## Alerts not firing

Verify:

* Alert rules loaded
* Metrics available
* Prometheus evaluation interval

---

## Health endpoint failure

Verify:

* Backend process
* Docker container status
* Application logs

---

# Best Practices

* Monitor dashboards continuously during production use.
* Investigate sustained alert conditions promptly.
* Review latency trends regularly.
* Track GPT token usage over time.
* Monitor Celery task failures and retries.
* Keep alert thresholds aligned with production behavior.

---

# Future Enhancements

Potential future additions include:

* Website generation throughput metrics
* Website generation duration metrics
* Queue wait time metrics
* Database query performance metrics
* Redis health metrics
* Business KPI dashboards
* Distributed tracing
* OpenTelemetry integration

---

# Summary

Website Wizard provides a comprehensive observability platform based on Prometheus, Grafana, structured metrics, health endpoints, and alerting.

This observability stack enables continuous monitoring of application health, performance, reliability, and operational behavior, supporting production operations and future scalability.
