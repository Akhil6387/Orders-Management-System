# Phase 5 – Tests & CI/CD

Complete test suite and CI/CD pipeline for the **Inventory & Order Management System**.

---

## Deliverables at a glance

```
phase5/
├── backend/
│   ├── pyproject.toml                   # pytest + coverage config
│   └── tests/
│       ├── conftest.py                  # expanded fixtures (ORM-level + factory helpers)
│       ├── test_exceptions.py           # unit: all custom exception classes
│       ├── test_product_service.py      # unit: ProductService (35 tests)
│       ├── test_order_service.py        # unit: OrderService   (28 tests)
│       ├── test_customer_service.py     # unit: CustomerService(28 tests)
│       └── test_api_integration.py      # integration: every HTTP endpoint (65 tests)
│
├── frontend/
│   ├── vite.config.js                   # Vitest config (merge into existing)
│   └── src/__tests__/
│       ├── setup.js                     # jest-dom bootstrapper
│       └── utils.test.js                # unit: helpers, pagination, formatting (28 tests)
│
├── .github/workflows/
│   ├── ci-cd.yml                        # full CI → staging → production pipeline
│   └── pr-checks.yml                    # fast lint + unit feedback on every PR
│
└── docker-compose.test.yml              # run full test stack locally with Postgres
```

---

## Running the backend tests locally

```bash
cd backend
pip install -r requirements.txt pytest-cov

# Fast (SQLite in-memory, ~5 s)
pytest

# With Postgres (mirrors CI)
TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_inventory pytest
```

Coverage HTML report is written to `backend/htmlcov/index.html`.

---

## Running the frontend tests locally

```bash
cd frontend

# 1. Add required devDependencies if not yet installed
npm install -D vitest @vitest/coverage-v8 jsdom \
  @testing-library/react @testing-library/user-event \
  @testing-library/jest-dom

# 2. Merge vite.config.js (test block) into your existing config, then:
npm test           # watch mode
npm test -- --run  # CI / one-shot

# Coverage
npm test -- --run --coverage
```

---

## Running with Docker (full Postgres stack)

```bash
# First time: create the shared network
docker network create inventory_network

# Start the test stack and run the suite
docker compose \
  -f docker-compose.yml \
  -f docker-compose.test.yml \
  run --rm test-runner
```

---

## CI/CD pipeline

### Triggers

| Event            | Workflows triggered                         |
|------------------|---------------------------------------------|
| Pull request     | `pr-checks.yml` (fast lint + unit tests)    |
| Push to develop  | `ci-cd.yml` → build → push → **staging**   |
| Push to main     | `ci-cd.yml` → build → push → **production** |

### Pipeline stages (`ci-cd.yml`)

```
backend-lint  ──┐
                ├── backend-test ──┬── backend-integration
frontend-test ──┘                  │
                                   └── docker-build ──┬── deploy-staging  (develop)
                                                       └── deploy-production (main, requires staging)
```

### Required GitHub secrets

| Secret                  | Used in                         |
|-------------------------|---------------------------------|
| `CODECOV_TOKEN`         | backend test (optional)         |
| `STAGING_HOST`          | deploy-staging                  |
| `STAGING_USER`          | deploy-staging                  |
| `STAGING_SSH_KEY`       | deploy-staging                  |
| `PRODUCTION_HOST`       | deploy-production               |
| `PRODUCTION_USER`       | deploy-production               |
| `PRODUCTION_SSH_KEY`    | deploy-production               |
| `SLACK_WEBHOOK_URL`     | deploy-production notifications |

### Required GitHub variables (per environment)

| Variable          | Example                          |
|-------------------|----------------------------------|
| `STAGING_URL`     | `https://staging.example.com`    |
| `PRODUCTION_URL`  | `https://app.example.com`        |

### Setting up deployment environments

1. Go to **Settings → Environments** in your GitHub repo.
2. Create `staging` and `production` environments.
3. Add the secrets above to each environment.
4. For `production`, enable **Required reviewers** to gate the deploy behind a manual approval.

---

## Coverage targets

| Layer       | Line coverage required |
|-------------|------------------------|
| Backend     | ≥ 80 %                 |
| Frontend    | ≥ 70 % (lines)         |

---

## Test design decisions

- **SQLite for unit/service tests** – fast, no external process, FK enforcement via pragma.
- **Postgres in CI integration stage** – validates NUMERIC precision, Enum handling, and real constraint behaviour.
- **ORM-level fixtures** (`persisted_product`, `persisted_order`, …) bypass the HTTP layer for service unit tests so failures are unambiguous.
- **`conftest.py` backward-compatible** – existing `sample_product` / `sample_customer` fixtures remain as aliases so the original test files (`test_products.py`, `test_orders.py`, `test_customers.py`) continue to pass without modification.
- **Frontend tests are pure-logic** – no DOM rendering required; Vitest runs them in Node/jsdom.
