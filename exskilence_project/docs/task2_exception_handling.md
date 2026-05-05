# Task 2: Global Exception Handling & Logging

## What is the task?
Implement centralized exception handling and logging so all API failures return a consistent JSON error contract. This task extends Task 1 by defining domain exceptions, global handlers, and logging behavior for business errors.

## Task requirements
- Add these required files:
  - `exceptions/base_exception.py`
  - `exceptions/validation_exception.py`
  - `exceptions/not_found_exception.py`
  - `exceptions/authorization_exception.py`
  - `middleware/error_handlers.py`
  - `config/logging_config.py`
- Define a shared base application exception with `message`, `status_code`, and `details` fields that child exceptions can reuse.
- Define exception-to-status mapping:
  - validation exception -> HTTP `400`
  - not found exception -> HTTP `404`
  - authorization exception -> HTTP `403`
- Global error handling requirements:
  - unknown API route such as `/api/<missing-path>` must return HTTP `404` with standard error JSON envelope.
  - all handled business exceptions must return standard error JSON envelope:
    - top-level `success: false`
    - `error.message` as the exception message
    - `error.details` as a list
- Preserve unknown route message for framework 404s:
  - when route is missing, response message must match Flask/Werkzeug default not-found message.
- Logging requirements:
  - business errors in 4xx flow must be logged at warning level with a log line that includes `"Business error"` and the exception message.
  - configure central logging in `config/logging_config.py` and wire it during app startup.
- Route behavior requirements in this task:
  - keep API routes returning JSON responses only (no HTML redirect for API errors).
  - no auth is required for existing Task 1 health route.
- Response contract requirements:
  - success envelope remains from Task 1.
  - error envelope must always include `success`, `error.message`, and `error.details`.
- Role/auth rules:
  - this task introduces authorization exception type and handler; actual login/role implementation is not required here.
- Data/validation rules:
  - validation failures must be represented through the validation exception and returned as HTTP `400` with `error.details` list.
- HTML template structure requirements:
  - no HTML template work is required in this task.
- CSS requirements:
  - no CSS work is required in this task.
- Layered responsibility boundaries:
  - route/controller layer: receives HTTP request and forwards to service; does not contain business validation logic.
  - service layer: raises domain exceptions when business rules fail.
  - repository layer: data access only; no HTTP response shaping.
  - utils/db layers: keep shared response helpers and database utilities centralized.
- Carry-forward requirements from Task 1 (must remain unchanged):
  - keep package-based layered structure in place.
  - keep `GET /api/health` behavior: HTTP `200`, `success: true`, `message`, and `data.status: "ok"`.
  - keep API success responses using a consistent success envelope.
- Local run and verification steps:
  - from `exskilence_project/`, install dependencies and start the app.
  - open `/api/health` and confirm Task 1 success envelope still works.
  - open an unknown `/api/...` route and confirm JSON error response with `success: false`, `error.message`, and `error.details` list.

## Objective of the task
Establish predictable API error behavior and centralized logging so business failures are handled consistently across routes while preserving Task 1 contracts and layered architecture boundaries.
