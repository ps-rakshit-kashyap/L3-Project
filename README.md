# TalentForge — AI-Powered Hiring Platform

**Phase 1: Project Foundation & Infrastructure**

TalentForge is an enterprise AI-powered hiring platform designed to orchestrate intelligent candidate discovery, automated resume evaluations, and structured interviews.

This repository represents **Phase 1: Project Foundation**, establishing a production-grade, modular foundation across frontend, backend, database connectivity, and containerization.

---

## Tech Stack

| Domain | Technology | Details |
|---|---|---|
| **Frontend** | [Next.js](https://nextjs.org/) 14 (App Router) | TypeScript, Vanilla CSS Design System, Modular Components |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | Python 3.12+, Pydantic v2 Settings, Structured Logging |
| **Database** | [PostgreSQL](https://www.postgresql.org/) | Relational database persistence |
| **ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) 2.x | Declarative Base, Connection Pooling with Pre-ping |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Database schema versioning |
| **Package Managers** | `pnpm` (Frontend), `uv` (Backend) | Fast, deterministic dependency management |
| **Containerization** | Docker & Docker Compose | Multi-container local orchestration |
| **Version Control** | Git | Clean commit boundaries |

---

## Project Structure

```
talentforge/
├── frontend/                     # Next.js App Router Application
│   ├── src/
│   │   ├── app/                  # App Router pages and layouts
│   │   │   ├── globals.css       # Custom design system tokens & styles
│   │   │   ├── layout.tsx        # Application root layout
│   │   │   └── page.tsx          # Landing page with live telemetry card
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── HealthStatusCard.tsx
│   │   │   └── SystemOverview.tsx
│   │   ├── services/             # API client layer
│   │   │   └── api.ts
│   │   └── types/                # TypeScript interfaces & types
│   │       └── health.ts
│   ├── scripts/                  # Automated verification scripts
│   ├── Dockerfile
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
├── backend/                      # FastAPI Backend Gateway
│   ├── app/
│   │   ├── main.py               # FastAPI application entrypoint & middleware
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic BaseSettings configuration
│   │   │   └── logging.py        # Structured logging setup
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py     # Version 1 route aggregator
│   │   │       └── health.py     # Health check endpoint
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy DeclarativeBase
│   │   │   └── session.py        # Database engine & session generator
│   │   ├── schemas/              # Pydantic data schemas
│   │   │   └── health.py
│   │   └── services/             # Business logic services (Phase 2+)
│   ├── alembic/                  # Alembic database migration environment
│   ├── tests/                    # Pytest test suite
│   ├── Dockerfile
│   ├── alembic.ini
│   └── pyproject.toml
├── docs/                         # System architecture & documentation
│   └── architecture.md
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore specifications
├── docker-compose.yml            # Docker Compose orchestration
└── README.md                     # Project documentation
```

---

## Environment Setup

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Configuration variables:

```ini
# Application Mode
APP_ENV=development

# Database Connection (PostgreSQL with psycopg 3 driver)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/talentforge

# Frontend & CORS
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Reserved for Future Phases
LLM_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

---

## Local Development Commands

### 1. Backend (FastAPI + uv)

```bash
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies in editable mode
uv pip install -e ".[dev]"

# Run database migrations
uv run alembic upgrade head

# Start FastAPI development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/api/v1/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### 2. Frontend (Next.js + pnpm)

```bash
cd frontend

# Install dependencies
pnpm install

# Start Next.js development server
pnpm dev
```

- Web Application: `http://localhost:3000`

---

## Docker Commands

Run the full stack (Frontend, Backend, and PostgreSQL database) via Docker Compose:

```bash
# Build and start all services in the background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# Stop all services
docker-compose down
```

Services started:
- `talentforge_postgres`: PostgreSQL 16 on port `5432`
- `talentforge_backend`: FastAPI on port `8000`
- `talentforge_frontend`: Next.js on port `3000`

---

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

Verifies API gateway availability and probes PostgreSQL database connectivity using `SELECT 1`.

#### Example Response (Healthy):
```json
{
  "status": "healthy",
  "api": "available",
  "database": "connected",
  "environment": "development",
  "version": "0.1.0",
  "timestamp": "2026-10-05T12:00:00.000000Z",
  "database_error": null
}
```

#### Example Response (Database Degraded):
```json
{
  "status": "degraded",
  "api": "available",
  "database": "disconnected",
  "environment": "development",
  "version": "0.1.0",
  "timestamp": "2026-10-05T12:00:00.000000Z",
  "database_error": "connection to server at '127.0.0.1', port 5432 failed"
}
```

---

## Running Tests

### Backend Tests
```bash
cd backend
.\.venv\Scripts\pytest.exe
```

### Backend Linting & Formatting
```bash
cd backend
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
```

### Frontend Verification & Contract Checks
```bash
cd frontend
pnpm test
```
