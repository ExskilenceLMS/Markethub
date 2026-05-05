# Task 4: Base Layout, Template Structure & UI Validation

## What is the task?
Build the shared web UI foundation with a reusable base layout, authentication pages, and global styling. This task adds server-rendered HTML flow while keeping API contracts and layered backend architecture from earlier tasks unchanged.

## Task requirements
- Implement web routes/pages with these behaviors:
  - `GET /` returns HTTP `200` and renders shared layout.
  - `GET /login` returns HTTP `200` and renders login form.
  - `GET /register` returns HTTP `200` and renders registration form.
  - `POST /login` with valid credentials returns redirect to `/` (HTTP `302`).
- Base template requirements (`templates/base.html`):
  - include `html`, `head`, `body`, and `main` elements.
  - include shared header and footer regions that render `site-header` and `site-footer`.
  - include shared stylesheet `base.css`.
  - include flash-messages partial in base template.
- Login template requirements (`templates/auth/login.html`):
  - include `form` with `method="post"`.
  - include `input[name="email"]` and `input[name="password"]`.
  - include `button[type="submit"]`.
  - include register navigation link.
  - include styling hooks using `card` and `btn`.
- Register template requirements:
  - show `Create account`.
  - include `input[name="name"]`, `input[name="email"]`, `input[name="password"]`.
  - include role field `name="role"` and customer option/value.
  - render with shared layout (`site-header` and `site-footer`).
- CSS requirements (`static/css/base.css`):
  - include selectors `.site-header`, `.site-footer`, `main`, `.card`, and `.btn`.
- Route behavior and auth expectations:
  - registration + logout + login flow must allow the same user to return to home page.
  - successful web login should redirect to home and not to login page.
- Response contract:
  - web pages use HTML responses and redirects.
  - API endpoints from earlier tasks keep their existing JSON envelope behavior.
- Role/auth rules:
  - keep customer-only self-registration rule.
  - keep session-based auth behavior for authenticated API routes.
- Data/validation rules:
  - preserve server-side validation and existing generic invalid-login message.
- Layered boundaries:
  - controller/route: HTTP forms, redirects, template rendering only.
  - service: business logic and auth rules.
  - repository: data access only.
  - utils/db layers: shared helpers and database operations.
- Carry-forward requirements from Tasks 1-3:
  - keep `GET /api/health` response contract unchanged.
  - keep global JSON error handling for unknown `/api/*` routes.
  - keep Task 3 auth API behavior and status codes unchanged.
- Local run and verification steps:
  - start app from `exskilence_project/`.
  - open `/` and confirm header, main content area, and footer appear.
  - open `/login` and verify POST form fields and submit button.
  - register a customer on `/register`, logout, login, and confirm redirect to `/`.

## Objective of the task
Create a consistent and reusable web presentation layer (templates + CSS + auth form flow) so future UI features can be built quickly without breaking existing API and auth behavior.
