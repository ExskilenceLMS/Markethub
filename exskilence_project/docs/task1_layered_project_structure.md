# Task 1: Layered Project Structure

## What is layered architecture?

Layered architecture organizes an application into horizontal layers, each with a narrow job. A request moves through the stack (for example, routes → services → repositories → database) instead of mixing HTTP handling, business rules, and SQL in one place.

## Why we use it for MarketHub

MarketHub is a layered monolith: one deployable app with clear internal boundaries. Layers keep the codebase easier to reason about as features (users, products, cart, orders) grow, and they match the responsibilities described in the E-commerce LLD (`docs/e_commerce.md`).

## Responsibility of each layer

| Layer | Folder | Responsibility |
| ----- | ------ | ---------------- |
| Routes | `routes/` | HTTP only: map URLs to handlers, call services, return responses. No business logic and no direct database access. |
| Services | `services/` | Business logic, orchestration, and rules. Calls repositories; does not run raw SQL. |
| Repositories | `repositories/` | Data access only: queries and persistence via the ORM/session. No business rules. |
| Models | `models/` | Database schema as ORM models and the shared SQLAlchemy `db` instance. |
| Validators | `validators/` | Input and payload validation (forms, JSON), reusable across routes/services. |
| Exceptions | `exceptions/` | Application-specific errors with stable messages and HTTP semantics. |
| Middleware | `middleware/` | Cross-cutting concerns such as global error handlers and future auth/logging hooks. |
| Config | `config/` | Environment-based settings (Flask, MySQL host/user/name/port, secrets). |
| Utils | `utils/` | Shared helpers (for example, a standard JSON API envelope). |

Supporting flow from the LLD:

```text
Routes → Services → Repositories → Models → Database
```

## Scalability and maintainability

- **Scalability of the codebase**: New features add files in the right layer instead of growing “god” modules. Teams can work on services and repositories in parallel with fewer merge conflicts.
- **Testability**: Services can be unit-tested with mocked repositories; repositories can be tested against the database without HTTP.
- **Maintainability**: When requirements change, you usually know which layer to edit. Swapping MySQL connection details or response format is localized to `config/` or `utils/`.
- **Production readiness**: Configuration is environment-driven (`FLASK_ENV`, `DB_HOST`, `DB_USER`, `DB_NAME`, etc.), the database is initialized in one place (`models/db.py` + `db.init_app`), and API responses share one shape (`utils/response.py`).

## What was set up in this task

- Package folders: `routes/`, `services/`, `repositories/`, `models/`, `validators/`, `exceptions/`, `middleware/`, `config/`, `utils/`.
- `config/settings.py`: development, production, and testing config classes; SQLAlchemy URI is built from `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and optional `DB_DRIVER` via `resolve_sqlalchemy_database_uri()` (see `.env.example`).
- SQLAlchemy via Flask-SQLAlchemy: `models/db.py`, wired in `app.py`.
- `app.py`: `create_app()` loads config, sets `SQLALCHEMY_DATABASE_URI` from env-based MySQL settings (production requires `DB_HOST`, `DB_USER`, `DB_NAME`), initializes `db`, registers middleware and blueprints.
- `utils/response.py`: `success_response` and `error_response` for consistent JSON.
- Example slice: `GET /api/health` uses a service only (no logic in the route beyond calling the service and formatting the response).

Run from `exskilence_project/` (with a virtualenv and `pip install -r requirements.txt`):

```bash
export FLASK_APP=app.py
flask run
```

Or: `python app.py`.
