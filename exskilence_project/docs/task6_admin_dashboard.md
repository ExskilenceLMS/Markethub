# Task 6: Admin Dashboard with Controlled UI Access

## Purpose

The admin dashboard is the **control surface** for platform operators: quick visibility into user counts and entry points to manage users, sellers, and categories as those modules are built. It must be reachable **only** by authenticated users whose role is **`admin`**.

## Role-based access

- **Routes:** Blueprint **`admin_bp`** (`routes/admin_routes.py`) uses **`url_prefix="/admin"`** and a **`before_request`** hook that calls **`UserService.require_roles(session, ["admin"])`**. Non-admins and guests receive a **flash** and **redirect** to **`web.login`**—no admin template is rendered.
- **Top navigation:** In **`templates/partials/navbar.html`**, the **Admin** link is wrapped in **`{% if session.get('role') == 'admin' %}`**, so sellers and customers never see admin navigation items.
- **Sidebar:** **`templates/partials/admin_sidebar.html`** is included only from **`admin/base_admin.html`**, which is used by admin pages only—there is no separate exposure of the sidebar to other roles.

## How stats are fetched and displayed

1. **`AdminService.get_dashboard_stats()`** (`services/admin_service.py`) builds a plain **dict** of counts.
2. **`UserRepository`** (`repositories/user_repository.py`) performs **`COUNT`** queries on **`users`** by role (`admin`, `seller`, `customer`) and total users—**no business rules** in the repository.
3. **`admin.dashboard`** passes **`stats=...`** into **`templates/admin/dashboard.html`**, which only **prints** values via the **`stat_card`** macro (`templates/partials/stat_card.html`).
4. **Products** and **orders** return **`0`** with hint text until those tables and repositories exist.

## Why a dashboard matters for admin control

Centralized metrics reduce time-to-diagnose issues (growth, role distribution) and anchor navigation for upcoming CRUD screens (**Users**, **Sellers**, **Categories**). Enforcing access at the **route** layer keeps the UI and API contract aligned with the layered monolith.

## URLs

| Path | Template |
| ---- | -------- |
| `/admin/` | `admin/dashboard.html` |
| `/admin/users` | `admin/users.html` (placeholder) |
| `/admin/sellers` | `admin/sellers.html` (placeholder) |
| `/admin/categories` | `admin/categories.html` (placeholder) |

Login redirect for admins points to **`admin.dashboard`** (`routes/web_routes.py`).

## Styling

**`static/css/style.css`** adds Flipkart-style **sidebar**, **stat grid**, and **stat cards**; **`main:has(.admin-layout)`** widens the content area for admin only so auth pages keep normal **`main`** padding.
