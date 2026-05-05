# Task 8: Product CRUD

## What is the task?
Add product management for both admin and seller web flows, including create/list/delete actions with role-based field visibility and validation.

## Task requirements
- Admin product form behavior:
  - `GET /admin/products/new` (admin session) returns HTTP `200` with form markup.
  - required admin form fields: `name`, `price`, `quantity`, `category_id`, `seller_id`.
  - page should use `form-card` layout hook.
- Admin create/list behavior:
  - `POST /admin/products/new` with valid data must redirect (HTTP `302`) to `/admin/products`.
  - created product name must appear on `/admin/products` list.
  - posting empty product name must return HTTP `200` and show `Product name is required`.
- Admin delete behavior:
  - `POST /admin/products/<id>/delete` removes product and redirects.
  - deleted product must no longer appear in admin list.
- Seller product form behavior:
  - seller with store-linked category can open `GET /staff/products/new` with HTTP `200`.
  - seller form must include `name`, `price`, and `category_id`.
  - seller form must not expose `seller_id` field.
  - seller form should use `form-card`.
- Seller create/list behavior:
  - `POST /staff/products/new` with valid data must redirect (HTTP `302`) to `/staff/products`.
  - created seller product must appear in seller product list.
- HTML template structure requirements:
  - `templates/admin/product_form.html` must include `form`, `input`, `textarea`, `select`, `label`, `button` and hooks `form-card`, `category_id`, `seller_id`, `price`.
  - `templates/staff/product_form.html` must include same core form controls with hooks `form-card`, `category_id`, `staff-hub--wide`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.data-table`, `.data-card`, `.form-card`, `.staff-hub--wide`.
- Role/auth rules:
  - admin can create/manage products across sellers.
  - seller can create/manage products for allowed seller scope.
- Response behavior:
  - valid form submissions redirect to list pages.
  - invalid form submissions re-render with validation messages.
- Data/validation rules:
  - product name is required.
  - product must include category and valid numeric fields for price/quantity.
- Layered boundaries:
  - route/controller: form parsing, role-gated route handling, render/redirect.
  - service: business validation, ownership/role checks, CRUD orchestration.
  - repository: product persistence and retrieval only.
  - utils/db: shared DB helpers and transactions.
- Carry-forward requirements from Tasks 1-7:
  - keep all previous API contracts and auth behavior unchanged.
  - keep admin dashboard/sidebars and category/store behavior unchanged.
  - keep seller read-only/store access behavior from Task 7 unchanged.
- Local run and verification steps:
  - as admin, open `/admin/products/new`, create product, verify it appears in `/admin/products`.
  - submit empty name and confirm validation message appears.
  - delete a created product and confirm it disappears from list.
  - as seller, open `/staff/products/new`, create product, verify redirect to `/staff/products`.

## Objective of the task
Enable full product CRUD workflows for admin and seller web portals with clear role boundaries, required form structure, and stable carry-forward behavior from previous tasks.
