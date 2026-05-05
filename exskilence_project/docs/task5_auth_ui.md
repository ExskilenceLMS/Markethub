# Task 5: Registration & Login UI

## What is the task?
Implement complete web authentication UI flows for login and registration with form validation feedback, role-aware redirects, and required auth page styling hooks.

## Task requirements
- Login page requirements (`GET /login`):
  - render HTTP `200` with `auth-page` and `auth-card` wrappers.
  - include POST form (`method="post"`), `input[name="email"]`, `input[name="password"]`.
  - include primary submit button styled with `btn-primary-fk`.
  - include visible link to register page.
- Register page requirements (`GET /register`):
  - render HTTP `200` with `auth-page` and `auth-card`.
  - include fields `name`, `email`, `password`, and `confirm_password`.
  - include role control `name="role"` (select/dropdown) with `customer` option.
  - include visible link back to login page.
- CSS requirements (`static/css/style.css`):
  - include selectors `.auth-page`, `.auth-card`, `.btn-primary-fk`, and `.auth-footer-link`.
- Web login behavior (`POST /login`):
  - on invalid password/credentials, return HTTP `200` and re-render login page with error summary.
  - show exact message `Invalid email or password`.
  - render error UI hooks such as `form-errors`.
- Web register behavior (`POST /register`):
  - when `password` and `confirm_password` do not match, return HTTP `200` and show `Passwords do not match`.
  - show field-level error for `confirm_password` (`err-confirm_password` or equivalent confirm_password error hook).
  - reject non-customer self-registration (for example role `seller`) and show message containing `Self-registration is only allowed`.
  - on valid customer registration, redirect with HTTP `302` to `/customer`.
- Role/auth rules:
  - self-service registration remains customer-only.
  - login continues using session-based authentication.
- Response contracts:
  - web auth routes return HTML pages on validation failure and redirects on success.
  - API auth routes from previous tasks keep existing JSON behavior unchanged.
- Data/validation rules:
  - validate confirm-password match on web registration.
  - keep generic login failure message to avoid exposing whether an email exists.
- HTML template structure requirements:
  - maintain reusable template inheritance and shared layout from Task 4.
  - include form structure and class hooks required above.
- Layered responsibility boundaries:
  - route/controller: read form data, call service, render/redirect.
  - service: validation and auth business logic.
  - repository: user data persistence/lookup only.
  - utils/db: password helper, error mapping, database plumbing.
- Carry-forward requirements from Tasks 1-4:
  - keep Task 1 health endpoint contract unchanged.
  - keep Task 2 API error envelope and status behavior unchanged.
  - keep Task 3 API auth endpoints and session behavior unchanged.
  - keep Task 4 base layout/header/footer structure and CSS hooks unchanged.
- Local run and verification steps:
  - open `/login` and `/register` to verify required fields/classes are present.
  - submit wrong password on login and confirm error text appears on same page.
  - submit mismatched passwords on register and confirm confirm_password error appears.
  - register valid customer and confirm redirect to `/customer`.

## Objective of the task
Deliver a learner-ready web auth experience with clear validation feedback and stable route behavior, while preserving all previously established API/auth contracts and layered architecture rules.
