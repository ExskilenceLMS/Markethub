# Task 9: Customer Dashboard

## What is the task?
Implement a customer-only web hub that shows account profile details, category browsing, and a product catalog view with category filtering.

## Task requirements
- Route and auth behavior:
  - `GET /customer/` must redirect guests to login (`302`).
  - logged-in customer must access `GET /customer/` with HTTP `200`.
  - non-customer roles (for example seller) must be redirected away from `/customer/*` routes.
  - customer login via `/login` must redirect to `/customer`.
- Customer dashboard requirements (`GET /customer/`):
  - render hooks/classes `customer-hub`, `customer-profile-card`, `customer-hub__nav`.
  - include text `My account`.
  - include navigation links to `/customer/categories` and `/customer/products`.
  - display logged-in customer email in the page.
- Customer categories page (`GET /customer/categories`) requirements:
  - return HTTP `200` for customer session.
  - render customer hub layout and page title/content for categories.
  - render `customer-category-grid` when data exists, or empty-state text like `No categories yet`.
- Customer products page (`GET /customer/products`) requirements:
  - return HTTP `200` for customer session.
  - render filter form with hook `customer-filter-form`.
  - include category filter control `select[name="category_id"]`.
  - render product container `customer-product-grid` and show available product names.
- HTML template structure requirements:
  - `templates/customer/dashboard.html` must include `h1`, `h2`, `nav`, `dl`, `dt`, `dd` and hooks `customer-hub`, `customer-profile-card`, `customer-hub__nav`.
  - `templates/customer/products.html` must include `form`, `select`, `ul`, `li`, `header` and hooks `customer-hub`, `customer-filter-form`, `customer-product-grid`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-hub`, `.customer-profile-card`, `.customer-product-card`, `.customer-filter-form`.
- Role/auth rules:
  - only customers can access customer routes.
  - customer area is read-only browsing (no create/update/delete actions).
- Data/validation rules:
  - catalog filtering uses category selection on customer products page.
- Layered responsibility boundaries:
  - route/controller: enforce customer access, read query params, render templates.
  - service: customer-facing business logic and catalog filtering rules.
  - repository: fetch user/category/product records only.
  - utils/db: shared DB/session helpers.
- Carry-forward requirements from Tasks 1-8:
  - preserve all API contracts and error envelope behavior.
  - preserve auth session/login/logout behavior.
  - preserve admin/staff/category/store/product management behaviors.
  - preserve required HTML/CSS hooks from previous tasks.
- Local run and verification steps:
  - log in as customer and confirm redirect to `/customer`.
  - open `/customer/categories` and `/customer/products` and verify required sections.
  - log in as seller (or use guest) and confirm `/customer/` redirects to login.

## Objective of the task
Provide a clean, customer-only storefront dashboard for profile and catalog browsing while maintaining strict role boundaries and all previously implemented platform behavior.
