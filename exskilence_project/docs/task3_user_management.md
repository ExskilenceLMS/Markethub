# Task 3: User Management (Admin, Staff, Customer)

## What is the task?
Build user registration, login, session-based authentication, and logout APIs using layered architecture. This task introduces role-aware registration rules and authenticated user lookup while preserving Task 1 and Task 2 behavior.

## Task requirements
- Implement and expose these authentication routes:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/auth/logout`
- Registration requirements (`POST /api/auth/register`):
  - accept JSON with `name`, `email`, `password`, and `role`.
  - allow self-registration only when `role` is `customer`.
  - reject non-customer self-registration (for example `admin`) with HTTP `400`.
  - on success, return HTTP `201` and success JSON envelope.
  - response `data` must include public user fields (for example `email`, `role`) and must not include `password` or `password_hash`.
- Login requirements (`POST /api/auth/login`):
  - accept JSON `email` and `password`.
  - on valid credentials, return HTTP `200` with success envelope and user public data.
  - create session/cookie-based login state so later `GET /api/auth/me` succeeds for the same client.
  - on invalid credentials, return HTTP `400` with exact message: `Invalid email or password`.
- Authenticated user endpoint (`GET /api/auth/me`) requirements:
  - when logged in, return HTTP `200` with current user data.
  - when unauthenticated, return HTTP `401` with standard error envelope and message containing `Authentication required`.
- Logout requirements (`POST /api/auth/logout`):
  - clear session state.
  - after logout, `GET /api/auth/me` must return HTTP `401`.
- Role/auth rules:
  - supported role values include `admin`, `seller`, and `customer`.
  - self-service registration is limited to `customer` only.
  - authentication state must rely on server session for protected `/api/auth/me`.
- Response contract requirements:
  - keep Task 1 success envelope structure.
  - keep Task 2 error envelope structure with `success: false`, `error.message`, and `error.details`.
- Data/validation requirements:
  - validate required registration/login fields.
  - keep password material private in API responses.
  - use generic login failure message to avoid account enumeration.
- HTML template structure requirements:
  - no HTML template work is required in this task.
- CSS requirements:
  - no CSS work is required in this task.
- Layered responsibility boundaries:
  - route/controller: parse request, manage HTTP/session boundary, return response.
  - service: authentication business logic (registration rules, password verification, auth checks).
  - repository: user persistence and lookup only.
  - utils/db: shared helpers (for example password hashing utility) and DB connectivity.
- Carry-forward requirements from earlier tasks (must remain unchanged):
  - Task 1: `GET /api/health` returns HTTP `200` with `success`, `message`, and `data.status = "ok"`.
  - Task 2: unknown `/api/*` routes return JSON error envelope with HTTP `404`.
  - Task 2: validation/not-found/authorization exception handling remains centralized with consistent error response shape.
- Local run and verification steps:
  - start the app from `exskilence_project/`.
  - call `/api/auth/register` with `role=customer` and confirm HTTP `201`.
  - call `/api/auth/login`, then `/api/auth/me` and confirm authenticated response.
  - call `/api/auth/logout`, then `/api/auth/me` and confirm HTTP `401`.
  - call login with wrong password and confirm `Invalid email or password`.

## Objective of the task
Deliver a secure and predictable user-auth foundation (registration, login, session identity, logout) that respects role constraints and layered architecture while preserving all established API contracts from previous tasks.
