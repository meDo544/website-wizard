# Website Wizard

Website Wizard is an AI-powered website generation platform that creates production-ready websites using GPT-driven content generation, automated processing pipelines, and a modern backend architecture.

Current Release: **v1.0.3**

---

## Features

* AI-powered website generation
* FastAPI REST API
* Celery background task processing
* PostgreSQL persistence
* Docker-based deployment
* Automated testing with pytest
* Prometheus metrics
* Grafana dashboards
* Health and readiness endpoints
* Production observability

---

## Technology Stack

* Python 3
* FastAPI
* Celery
* PostgreSQL
* SQLAlchemy
* Docker & Docker Compose
* Prometheus
* Grafana
* OpenAI API

---

## Documentation

Comprehensive project documentation is available in the `docs/` directory.

| Document                       | Description                      |
| ------------------------------ | -------------------------------- |
| `docs/README.md`               | Project overview                 |
| `docs/ARCHITECTURE.md`         | System architecture              |
| `docs/PIPELINE.md`             | Website generation pipeline      |
| `docs/DATABASE.md`             | Database design                  |
| `docs/API.md`                  | API reference                    |
| `docs/DEPLOYMENT.md`           | Deployment guide                 |
| `docs/OPERATIONS.md`           | Operations guide                 |
| `docs/RECOVERY.md`             | Recovery procedures              |
| `docs/SECURITY.md`             | Security practices               |
| `docs/CONTRIBUTING.md`         | Contribution guidelines          |
| `docs/OBSERVABILITY.md`        | Monitoring and observability     |
| `docs/CHANGELOG.md`            | Project changelog                |
| `docs/RELEASE_NOTES_v1.0.0.md` | Initial production release notes |

---

## Running the Project

Start the application:

```bash
docker compose up -d
```

Run the automated test suite:

```bash
source venv/bin/activate
python -m pytest tests/ -q
```

---

## Current Engineering Status

* ✅ Production Platform (v1.0.0)
* ✅ Documentation Foundation (v1.0.1)
* ✅ Automated Testing (v1.0.2)
* ✅ Observability Pack (v1.0.3)

---

## License

Refer to the project repository for licensing information.
