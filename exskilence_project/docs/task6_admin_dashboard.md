# Task 6: Admin Dashboard with Controlled UI Access

## What is the task?
Build an admin-only web dashboard with sidebar navigation and statistics cards, while enforcing strict role-based access and preserving all previous auth/API behavior.

## Task requirements
- Route and access behavior:
  - `GET /admin/` for unauthenticated users must return redirect (HTTP `302`) to login page.
  - `GET /admin/` for logged-in non-admin users (for example customer) must return redirect (HTTP `302`) to login page.
  - admin login through `POST /login` must redirect to `/admin` (or `/admin/`).
  - `GET /admin/users` must be accessible for admin session and return HTTP `200`.
- Admin dashboard page requirements (`templates/admin/dashboard.html`):
  - render admin shell hooks: `admin-layout` and `admin-sidebar`.
  - include dashboard copy/title containing `Admin dashboard`.
  - include page/header structure with identifiers `admin-page-header`, `page-title`.
  - include statistics section using `stat-grid`.
  - dashboard must render multiple stat cards (`stat-card`) and labels such as `Total users`, `Admins`, and `Customers`.
- Admin sidebar requirements (`templates/partials/admin_sidebar.html`):
  - include `aside`, `nav`, and link elements.
  - include hooks `admin-sidebar` and `admin-sidebar__link`.
  - include links for dashboard, users, sellers, and categories.
- Stat-card partial requirements (`templates/partials/stat_card.html`):
  - include markup with hooks `stat-card`, `stat-card__label`, and `stat-card__value`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.admin-layout`, `.admin-sidebar`, `.admin-main`, `.stat-card`, `.stat-grid`.
- Response/redirect expectations:
  - unauthorized admin-area access should redirect to login web route.
  - authorized admin access should render HTML (not JSON error) for admin web pages.
- Role/auth rules:
  - only `admin` role can access `/admin/*` routes.
  - customer/seller/guest must be blocked from admin pages.
- Data/validation rules:
  - dashboard statistics are sourced from backend counts and rendered in UI cards.
- Layered responsibility boundaries:
  - route/controller: role guard, HTTP redirects, template rendering.
  - service: compute dashboard stats and admin business logic.
  - repository: count/query user data only.
  - utils/db: shared database/session helpers.
- Carry-forward requirements from Tasks 1-5:
  - keep all existing API contracts (health + auth + error envelope) unchanged.
  - keep customer-only self-registration and session auth behavior unchanged.
  - keep Task 4 base layout/auth UI structure working.
  - keep Task 5 auth UI selectors and validation messaging behavior.
- Local run and verification steps:
  - open `/admin/` as guest and confirm redirect to `/login`.
  - log in as customer and verify `/admin/` still redirects to `/login`.
  - log in as admin and confirm redirect to `/admin`, dashboard renders with sidebar and stat grid.
  - open `/admin/users` and confirm page renders under admin layout.

## Objective of the task
Deliver a secure admin web shell with enforced role access and dashboard visibility so operational/admin features can be added on top of a stable, protected layout.
