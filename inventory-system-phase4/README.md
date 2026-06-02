# Inventory & Order Management System

A production-ready, full-stack Inventory & Order Management System built with **FastAPI**, **React**, and **PostgreSQL** — fully containerized with Docker and deployable to Render + Vercel.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Quick Start (Docker)](#quick-start-docker)
6. [Local Development](#local-development)
7. [Environment Variables](#environment-variables)
8. [API Documentation](#api-documentation)
9. [Business Rules](#business-rules)
10. [Testing](#testing)
11. [Deployment Guide](#deployment-guide)
    - [Backend → Render](#backend--render)
    - [Frontend → Vercel](#frontend--vercel)
12. [CI/CD](#cicd)
13. [Project Structure](#project-structure)

---

## Project Overview

A business-facing inventory system that lets teams manage **products**, **customers**, and **orders** with real-time stock tracking, atomic order processing, and a modern responsive UI.

---

## Features

| Area         | Capabilities |
|--------------|-------------|
| Products     | CRUD, SKU uniqueness, stock tracking, low-stock alerts |
| Customers    | CRUD, email uniqueness, order history |
| Orders       | Create with multiple line items, atomic stock deduction, order history |
| Dashboard    | KPI cards (products / customers / orders / low-stock), charts |
| API          | RESTful, Pydantic validation, standardized error responses |
| Docker       | Multi-stage builds, non-root containers, health checks |
| Security     | CORS, ORM-based SQL injection protection, secrets via env vars |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP :80
┌───────────────────────────▼─────────────────────────────┐
│              Nginx (frontend container)                  │
│   Serves React SPA  │  Proxies /api/* → backend:8000    │
└──────────┬──────────────────────────────────────────────┘
           │                         │ proxy
    React SPA                        ▼
  (client-side             ┌─────────────────────┐
   routing)                │  FastAPI  :8000      │
                           │  SQLAlchemy ORM      │
                           │  Alembic Migrations  │
                           └──────────┬──────────┘
                                      │ TCP :5432
                           ┌──────────▼──────────┐
                           │   PostgreSQL 16      │
                           │   (named volume)     │
                           └─────────────────────┘

All three services run on the same Docker bridge network: app_network
```

---

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Frontend       | React 18, Vite, React Router, Axios, Material UI |
| Backend        | Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic v2 |
| Database       | PostgreSQL 16                     |
| Containerization | Docker, Docker Compose          |
| Web Server     | Nginx (alpine)                    |
| CI/CD          | GitHub Actions                    |
| Backend Deploy | Render                            |
| Frontend Deploy | Vercel                           |

---

## Quick Start (Docker)

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourname/inventory-system.git
cd inventory-system

# 2. Create your .env from the example
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and SECRET_KEY at minimum

# 3. Build and start all services
docker compose up --build

# 4. Open the application
#    Frontend:  http://localhost
#    API docs:  http://localhost:8000/docs
#    ReDoc:     http://localhost:8000/redoc
```

To run in detached mode:

```bash
docker compose up --build -d
docker compose logs -f    # stream logs
```

To stop and remove containers:

```bash
docker compose down              # keep the postgres volume
docker compose down -v           # also delete the postgres volume
```

---

## Local Development

Run each service independently for faster iteration.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # configure DATABASE_URL to local postgres

# Run migrations
alembic upgrade head

# Start dev server with reload
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env             # set VITE_API_URL=http://localhost:8000

npm run dev                      # starts at http://localhost:5173
```

### PostgreSQL (local, without Docker)

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16
createdb inventory_db

# Ubuntu
sudo apt install postgresql-16
sudo -u postgres createdb inventory_db
```

---

## Environment Variables

All variables are documented in `.env.example`.

| Variable            | Service   | Description |
|---------------------|-----------|-------------|
| `POSTGRES_USER`     | postgres  | DB username |
| `POSTGRES_PASSWORD` | postgres  | DB password (**change this!**) |
| `POSTGRES_DB`       | postgres  | Database name |
| `DATABASE_URL`      | backend   | Full SQLAlchemy connection string |
| `APP_ENV`           | backend   | `development` \| `production` \| `test` |
| `SECRET_KEY`        | backend   | Random hex string for signing (32+ bytes) |
| `CORS_ORIGINS`      | backend   | Comma-separated list of allowed origins |
| `VITE_API_URL`      | frontend  | Backend base URL (build-time) |

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Documentation

Interactive Swagger UI is available at `/docs` when the backend is running.

### Base URL

```
http://localhost:8000        (local Docker)
https://your-service.onrender.com   (production)
```

### Products

| Method | Endpoint           | Description         |
|--------|--------------------|---------------------|
| POST   | `/products`        | Create product      |
| GET    | `/products`        | List all products   |
| GET    | `/products/{id}`   | Get product by ID   |
| PUT    | `/products/{id}`   | Update product      |
| DELETE | `/products/{id}`   | Delete product      |

**Create product request body:**
```json
{
  "product_name": "Widget A",
  "sku": "WGT-001",
  "price": 19.99,
  "quantity_in_stock": 100
}
```

### Customers

| Method | Endpoint            | Description        |
|--------|---------------------|--------------------|
| POST   | `/customers`        | Create customer    |
| GET    | `/customers`        | List all customers |
| GET    | `/customers/{id}`   | Get customer by ID |
| DELETE | `/customers/{id}`   | Delete customer    |

### Orders

| Method | Endpoint          | Description      |
|--------|-------------------|------------------|
| POST   | `/orders`         | Create order     |
| GET    | `/orders`         | List all orders  |
| GET    | `/orders/{id}`    | Get order by ID  |
| DELETE | `/orders/{id}`    | Delete order     |

**Create order request body:**
```json
{
  "customer_id": 1,
  "items": [
    { "product_id": 3, "quantity": 2 },
    { "product_id": 7, "quantity": 1 }
  ]
}
```

### Error Response Format

```json
{
  "success": false,
  "message": "Insufficient stock for product SKU WGT-001",
  "error_code": "INSUFFICIENT_STOCK"
}
```

### Common Error Codes

| Code                  | HTTP Status | Trigger |
|-----------------------|-------------|---------|
| `PRODUCT_NOT_FOUND`   | 404         | Product ID doesn't exist |
| `CUSTOMER_NOT_FOUND`  | 404         | Customer ID doesn't exist |
| `ORDER_NOT_FOUND`     | 404         | Order ID doesn't exist |
| `DUPLICATE_SKU`       | 409         | SKU already in use |
| `DUPLICATE_EMAIL`     | 409         | Email already registered |
| `INSUFFICIENT_STOCK`  | 422         | Not enough stock for order |
| `VALIDATION_ERROR`    | 422         | Request body fails schema validation |

---

## Business Rules

1. **SKU uniqueness** — duplicate SKU returns `409 DUPLICATE_SKU`
2. **Email uniqueness** — duplicate email returns `409 DUPLICATE_EMAIL`
3. **Non-negative stock** — `quantity_in_stock` cannot go below 0
4. **Stock check on order** — each line item is validated before any DB write
5. **Atomic stock deduction** — all stock updates in a single transaction; any failure rolls back everything
6. **Backend-calculated total** — `total_amount` is computed server-side (`Σ quantity × unit_price`)
7. **Atomic transactions** — orders use SQLAlchemy transactions with automatic rollback on error

---

## Testing

### Backend

```bash
cd backend
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

Tests are located in:

```
backend/tests/
├── test_products.py     # API-level product tests
├── test_customers.py    # API-level customer tests
├── test_orders.py       # API-level order + stock tests
└── services/
    ├── test_product_service.py
    └── test_order_service.py
```

### Frontend

```bash
cd frontend
npm test                 # Vitest unit tests
npm run test:coverage    # with coverage
```

---

## Deployment Guide

### Backend → Render

**Option A — Render Blueprint (recommended)**

```bash
# Push your repo to GitHub, then in Render dashboard:
# New → Blueprint → connect your repo → Render reads render.yaml automatically
```

**Option B — Manual**

1. New Web Service → connect GitHub repo
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add a PostgreSQL add-on; Render injects `DATABASE_URL` automatically
6. Add env vars: `SECRET_KEY`, `CORS_ORIGINS`, `APP_ENV=production`

### Frontend → Vercel

**Option A — Vercel CLI**

```bash
npm i -g vercel
cd frontend
vercel deploy --prod
# Follow the prompts; set VITE_API_URL to your Render backend URL
```

**Option B — Vercel Dashboard**

1. Import Git Repository → select your repo
2. Root Directory: `frontend`
3. Framework Preset: **Vite**
4. Add environment variable: `VITE_API_URL` = `https://your-service.onrender.com`
5. Deploy

> `vercel.json` at the project root handles SPA rewrites and cache headers automatically.

### Post-Deployment

Update backend `CORS_ORIGINS` to include your Vercel production URL:

```
CORS_ORIGINS=https://your-project.vercel.app
```

---

## CI/CD

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs on every push:

| Job               | Trigger         | Steps |
|-------------------|-----------------|-------|
| `backend-test`    | Every push      | Install → migrate → pytest |
| `frontend-build`  | Every push      | npm ci → vite build |
| `docker-build`    | After tests pass | docker compose build |
| `deploy-backend`  | Push to `main`  | Trigger Render deploy hook |
| `deploy-frontend` | Push to `main`  | `vercel deploy --prod` |

Required GitHub Secrets:

| Secret                | Description |
|-----------------------|-------------|
| `RENDER_API_KEY`      | Render account API key |
| `RENDER_SERVICE_ID`   | Render service ID for the backend |
| `VERCEL_TOKEN`        | Vercel personal access token |
| `VERCEL_ORG_ID`       | Vercel org/user ID |
| `VERCEL_PROJECT_ID`   | Vercel project ID |

---

## Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (FastAPI routers)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Database queries (repository pattern)
│   │   ├── core/          # Config, exceptions, logging
│   │   ├── database/      # Engine, session factory
│   │   ├── utils/         # Shared utilities
│   │   └── main.py        # FastAPI app factory
│   ├── tests/             # Pytest test suite
│   ├── alembic/           # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios clients
│   │   ├── pages/         # Route-level page components
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   ├── context/       # React Context providers
│   │   ├── layouts/       # Page layout wrappers
│   │   ├── routes/        # React Router config
│   │   └── App.jsx
│   ├── nginx.conf         # Production Nginx config
│   ├── Dockerfile
│   └── .env.example
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions pipeline
│
├── docker-compose.yml             # Production compose
├── docker-compose.override.yml    # Dev overrides (hot-reload)
├── render.yaml                    # Render Blueprint
├── vercel.json                    # Vercel config
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md
```

---

## License

MIT © 2024
