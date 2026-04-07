# Task 3: User Management (Admin, Staff, Customer)

This aligns with the MarketHub layered monolith in `docs/e_commerce.md` (LLD reference: `Docs/ecommerce_lld.md` if present).

## User roles and responsibilities

| Role | Value (`role` column) | Typical responsibility |
| ---- | --------------------- | ---------------------- |
| Admin | `admin` | Platform administration (future: user/category/seller management). |
| Seller (staff) | `seller` | Store staff: products, inventory, orders (future modules). |
| Customer | `customer` | Browse, cart, checkout (future modules). |

**Self-service registration** (`POST /api/auth/register`) only allows `customer`. Admin and seller accounts are not created through this public endpoint (role-based validation in `validators/user_validator.py`).

## Authentication flow: register → login

1. **Register** — Client sends JSON `{ "name", "email", "password", "role": "customer" }`. The route delegates to `UserService.register`, which validates input, ensures the email is unique, hashes the password, and persists via `UserRepository`. Response returns public user fields (no password or hash).

2. **Login** — Client sends `{ "email", "password" }`. `UserService.login` loads the user by email, verifies the password against the stored hash, and returns public user data. The route stores `user_id`, `role`, `name`, and `email` in the **Flask signed cookie session** (`session.permanent` uses `PERMANENT_SESSION_LIFETIME` from config).

3. **Session** — `GET /api/auth/me` requires a session with `user_id`; the service loads the user from the database again for up-to-date fields. `POST /api/auth/logout` clears the session.

4. **Guards** — `UserService.require_authenticated(session)` and `UserService.require_roles(session, ["admin", ...])` are available for future routes (401 vs 403 via `AuthorizationException`).

## Model → repository → service → routes

```text
routes/auth_routes.py
    → UserService (business rules, password hashing orchestration)
        → UserRepository (SQLAlchemy `session` / `select` / `get`, commits)
            → models/user.py (table shape, `to_public_dict`)
```

- **Routes** parse JSON and call services; they do not hash passwords or query the DB.
- **Services** call validators, repositories, and `utils/passwords`; they raise `ValidationException`, `NotFoundException`, or `AuthorizationException` as appropriate.
- **Repositories** perform persistence and lookups only; no business rules.
- **Validators** hold reusable input checks (email format, required fields, self-register role).

## Password hashing and validation

- Passwords are **never** stored in plain text. `utils/passwords.py` uses **Werkzeug** `generate_password_hash` / `check_password_hash` (industry-standard salted hashing for Flask apps).
- **Validation** ensures email shape, non-empty password, unique email on register, and allowed role for registration. Login uses a **single generic error** (“Invalid email or password”) so callers cannot infer whether an email exists.

## API surface (JSON)

| Method | Path | Purpose |
| ------ | ---- | ------- |
| POST | `/api/auth/register` | Create customer account |
| POST | `/api/auth/login` | Verify credentials, start session |
| POST | `/api/auth/logout` | End session |
| GET | `/api/auth/me` | Current user (requires session) |

## Configuration

- `SECRET_KEY` must be set for production so sessions are signed correctly.
- Session cookie options: `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, `SESSION_COOKIE_SECURE` (enabled in production config when `SESSION_COOKIE_SECURE` env is not overridden to false).
- Tables are created on startup via `db.create_all()` inside `create_app` (suitable for development; use migrations for production).
