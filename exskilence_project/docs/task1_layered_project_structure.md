# Task 1: Layered Project Structure

## What is the task?
Set up the foundational layered project structure and wire a working health API endpoint. This task establishes the folder/package layout, response contract, and HTTP-to-service flow that all later tasks must follow.

## Task requirements
- Create these package directories at project root and include `__init__.py` inside each: `routes/`, `services/`, `repositories/`, `models/`, and `config/`.
- Create `utils/response.py` and provide a standard success JSON envelope helper used by API routes.
- Create `routes/health.py` and `services/health_service.py`, and wire them so the route calls the service (route handles HTTP; service contains business logic).
- Implement `GET /api/health` to return HTTP `200` with JSON that includes:
  - `success: true`
  - a `message` field (non-empty, string)
  - `data.status: "ok"`
- Keep unknown API paths under `/api/*` returning a JSON error body through global API error handling (do not redirect to HTML pages for unknown API routes).
- Response contract requirement for this task:
  - successful API responses must follow a consistent envelope shape (including `success`, `message`, and `data`).
- Role/auth requirement:
  - no authentication requirement is needed for `GET /api/health` in this task.
- Data and validation requirement:
  - no request body or query validation is required for `GET /api/health`; it is a read-only availability check.
- HTML template structure requirements:
  - no HTML template creation is required in this task.
- CSS requirements:
  - no CSS work is required in this task.
- Layered responsibility boundaries (must be followed):
  - route/controller layer: HTTP handling only (request/response, status code, blueprint wiring).
  - service layer: business logic only.
  - repository layer: data access only (for future tasks; no business logic).
  - utils/db layers: shared helpers and database utilities as defined by project structure.
- Local run and verification steps:
  - from `exskilence_project/`, install dependencies.
  - start the app with `flask run` (with `FLASK_APP=app.py`) or `python app.py`.
  - open `/api/health` in the browser and confirm a JSON response with `success`, `message`, and `data.status = "ok"`.
  - open a non-existing `/api/...` URL and confirm a JSON error body is returned.

## Objective of the task
Build a clean layered baseline that enforces separation of concerns and provides a stable API response pattern, so all upcoming features can be implemented consistently without changing core Task 1 behavior.
