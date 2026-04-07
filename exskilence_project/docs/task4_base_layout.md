# Task 4: Base Layout, Template Structure & UI Validation

Aligned with the MarketHub LLD (`docs/e_commerce.md`). Server-rendered pages live under the same Flask app as JSON APIs; routes call **services** for validation and persistence, templates only **display** data and errors.

## Template inheritance (Jinja2)

Child templates use `{% extends "base.html" %}` and fill `{% block content %}` (and optional blocks like `title`, `head_extra`). Shared chrome (navbar, footer, flash area) lives in **`templates/base.html`**, so pages stay consistent without copying markup.

## Why a base layout matters

One layout enforces the same navigation, footer, and message area everywhere. New screens only implement `content` (and related blocks), which scales as admin, staff, and customer areas grow.

## Flash messages

Server code calls `flash(message, category)` (e.g. `success`, `warning`, `danger`). **`templates/partials/flash_messages.html`** uses `get_flashed_messages(with_categories=true)` and renders a dismissible-style strip per category. Flashes are consumed on the next request that renders the layout—ideal for redirects after login/logout.

## Showing backend validation in the UI

- **No business rules in templates.** Forms POST to routes; **`UserService`** raises **`ValidationException`** with `message` and optional **`details`** (field names or structures).
- **`utils/form_errors.py`** maps exceptions to a **`form_errors`** dict: `field_name -> [messages]` and **`_form`** for non-field / general errors.
- **`templates/partials/form_errors.html`** defines macros:
  - **`form_error_summary`**: general errors (`_form` only).
  - **`field_errors`**: list under a specific input; inputs get a `user-error` class when that field has errors.

HTML forms use **`novalidate`** so the browser does not override server-driven validation; the service remains the source of truth.

## Role-based UI rendering

**`session`** (populated after login) exposes `role`. **`templates/partials/navbar.html`** uses Jinja `{% if session.get('role') == 'admin' %}` (and seller/customer) to show only relevant links. Unauthorized areas (e.g. `/admin`) are still enforced in **`routes/web_routes.py`** via **`UserService.require_roles`**, which raises **`AuthorizationException`**—the route flashes a message and redirects to login.

## File map

| Path | Role |
| ---- | ---- |
| `templates/base.html` | Root layout, blocks, static CSS |
| `templates/partials/navbar.html` | Role-aware nav + auth links |
| `templates/partials/footer.html` | Footer |
| `templates/partials/flash_messages.html` | Global flashes |
| `templates/partials/form_errors.html` | Error macros |
| `templates/auth/login.html`, `register.html` | Auth forms |
| `templates/admin/`, `staff/`, `customer/` | Sample role pages |
| `routes/web_routes.py` | HTML routes (calls `UserService`, passes `form_errors`) |
| `static/css/base.css` | Shared styles |

## URLs (HTML)

- `/` — Home  
- `/login`, `/register`, `/logout` — Session auth  
- `/admin`, `/staff`, `/customer` — Role placeholders (guarded)

JSON APIs remain under `/api/…`.
