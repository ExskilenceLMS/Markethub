# Task 7: Category & Store UI (Structured Forms)

## What is the task?
Implement admin-side category and store management forms (with validation and redirects) plus seller read-only store visibility pages.

## Task requirements
- Category form route behavior:
  - `GET /admin/categories/new` (admin session) returns HTTP `200` with structured form.
  - form must include `form-card`, `method="post"`, `input[name="name"]`, `textarea[name="description"]`.
  - `POST /admin/categories/new` with valid data redirects (HTTP `302`) to `/admin/categories`.
  - created category name must appear on `/admin/categories` list page.
  - posting empty name must re-render form with `Category name is required` and validation UI hooks (`form-errors` or `field-error`).
- Store form route behavior:
  - `GET /admin/stores/new` (admin session) returns HTTP `200` with structured form.
  - form must include `form-card`, `select[name="seller_id"]`, `input[name="category_ids"]` checkboxes inside `checkbox-grid`, and `input[name="is_active"]`.
  - `POST /admin/stores/new` with valid values redirects (HTTP `302`) to `/admin/stores`.
  - created store name must appear on `/admin/stores` list page.
- Seller read-only behavior:
  - authenticated seller can open `GET /staff/stores` and see stores view content (for example `Your stores`).
- Required HTML structure:
  - `templates/admin/category_form.html` must include `form`, `input`, `textarea`, `label`, `button` and hooks `form-card`, `name`, `description`.
  - `templates/admin/store_form.html` must include `form`, `select`, `fieldset`, `input`, `label` and hooks `form-card`, `seller_id`, `checkbox-grid`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.form-card`, `.checkbox-grid`, `.checkbox-label`, `.form-label-block`.
- Role/auth rules:
  - only admin can create categories/stores under `/admin/*`.
  - seller can access read-only staff stores area.
- Response expectations:
  - valid admin create actions redirect to list routes.
  - invalid submissions re-render same form with validation feedback.
- Data/validation rules:
  - category name is required.
  - store creation requires valid seller/category selection handling.
- Layered boundaries:
  - route/controller: parse form inputs and redirect/render.
  - service: validation and business rules for category/store creation.
  - repository: category/store/user data access only.
  - utils/db: shared helpers and persistence plumbing.
- Carry-forward requirements from Tasks 1-6:
  - keep health API contract unchanged.
  - keep global API error envelope/exception behavior unchanged.
  - keep auth API and web auth UI behavior unchanged.
  - keep admin access guard and dashboard layout behavior unchanged.
- Local run and verification steps:
  - log in as admin and open `/admin/categories/new` and `/admin/stores/new`.
  - submit valid category/store forms and verify redirect + list appearance.
  - submit invalid category (empty name) and confirm validation message.
  - log in as seller and open `/staff/stores` to confirm read-only page access.

## Objective of the task
Provide a production-style admin management UI for categories and stores with proper validation, redirects, and role-based access while preserving all previously delivered app behavior.
