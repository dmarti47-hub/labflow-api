# LabFlow API

Production-style REST API for tracking mock clinical lab sample workflows.

LabFlow API is a backend portfolio project built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker, JWT authentication, role-based access control, audit logging, QC notes, reporting endpoints, automated tests, Ruff linting, and GitHub Actions CI.

This project uses mock/non-patient data only.

---

## Why I Built This

I built LabFlow API to connect my clinical molecular laboratory background with backend software development. The project models a realistic lab sample workflow, including accessioning, sample status progression, QC review, priority handling, audit history, and operational reporting.

The goal was to build more than basic CRUD endpoints. LabFlow API includes persistence, validation, authentication, authorization, migrations, Dockerized services, and automated testing.

---

## Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* JWT authentication
* Docker and Docker Compose
* pytest
* Ruff
* GitHub Actions

---

## Features

* User registration and login
* JWT bearer token authentication
* Role-based access control
* Admin-only soft deletes
* Sample creation, listing, filtering, sorting, updating, and soft deletion
* QC notes for sample review workflows
* Audit logging for workflow changes
* Operational reporting endpoints
* PostgreSQL persistence
* Alembic database migrations
* Dockerized local setup
* Automated test suite

---

## Sample Statuses

Samples can move through these statuses:

* received
* processing
* qc_review
* resulted
* cancelled

---

## Sample Priorities

Samples support these priorities:

* routine
* urgent
* repeat

---

## API Endpoints

### Auth

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Samples

```text
GET    /samples
POST   /samples
GET    /samples/{id}
PATCH  /samples/{id}
DELETE /samples/{id}
```

### QC Notes

```text
POST /samples/{id}/qc-notes
GET  /samples/{id}/qc-notes
```

### Audit Logs

```text
GET /audit-log/{sample_id}
```

### Reports

```text
GET /reports/status-summary
GET /reports/test-type-summary
GET /reports/overdue
```

---

## Local Setup

Clone the repository:

```bash
git clone https://github.com/dmarti47-hub/labflow-api.git
cd labflow-api
```

Copy the environment template:

```bash
cp .env.example .env
```

Start the app:

```bash
docker compose up -d --build
```

Seed development users:

```bash
docker compose exec api uv run python -m scripts.create_dev_users
```

Open the API docs:

```text
http://localhost:8000/docs
```

---

## Development Users

```text
admin@example.com / AdminPassword123!
tech@example.com  / StrongPassword123!
```

---

## Running Tests

Start the test database:

```bash
docker compose --profile test up -d db_test
```

Run tests:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

---

## Useful Commands

Start the full app:

```bash
docker compose up -d --build
```

Stop containers:

```bash
docker compose down
```

View API logs:

```bash
docker compose logs -f api
```

View database logs:

```bash
docker compose logs -f db
```

Run migrations:

```bash
docker compose exec api uv run alembic upgrade head
```

Seed dev users:

```bash
docker compose exec api uv run python -m scripts.create_dev_users
```

Run local development server:

```bash
uv run uvicorn app.main:app --reload
```

---

## Overdue Sample Rules

| Priority | Overdue After |
| -------- | ------------: |
| urgent   |      24 hours |
| repeat   |      48 hours |
| routine  |      72 hours |

Resulted, cancelled, and soft-deleted samples are excluded from overdue reports.

---

## Project Status

Implemented:

* FastAPI application
* PostgreSQL database
* SQLAlchemy models
* Alembic migrations
* JWT authentication
* Role-based access control
* Sample workflow endpoints
* QC note endpoints
* Audit logging
* Reporting endpoints
* Docker Compose setup
* Automated pytest suite
* Ruff linting
* GitHub Actions CI

Planned improvements:

* API documentation screenshots
* Test coverage badge
* CSV export endpoint
* Admin user management endpoints
* Cloud deployment

---