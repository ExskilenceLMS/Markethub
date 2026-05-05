# Task 14: Order Tracking System

## What is the task?
Build order tracking views and filters for customer, admin, and staff with strict role-based visibility and secure order-detail access.

## Task requirements
- Customer tracking route behavior:
  - guest `GET /customer/orders` must redirect to login.
  - logged-in customer can open `GET /customer/orders` and see order tracking list.
  - `GET /customer/orders?status=Placed` must render filtered tracking view.
  - customer detail page `GET /customer/orders/<id>` must show order number/title, status, and total.
  - customer must not access another customer’s order detail; redirect to `/customer/orders`.
- Admin/staff tracking behavior:
  - `GET /admin/orders?status=Placed` must render list with status filter controls and matching rows.
  - `GET /staff/orders?status=Placed` must render list with status filter controls and matching rows.
- Tracking list UI requirements (`templates/customer/orders.html`):
  - include heading `My orders`.
  - include tracking columns including `Status` and `Details`.
  - include `form` status filter labeled `Filter by status`.
  - include hooks `customer-hub`, `customer-filter-form`, `data-table`.
- Customer order detail UI requirements (`templates/customer/order_detail.html`):
  - include detail title like `Order #<id>`.
  - include fields for `Status`, `Total`, and placed timestamp information.
  - include hooks `customer-hub`, `customer-profile-dl`, `page-title`.
- HTML structure requirements:
  - `templates/customer/orders.html` must include `h1`, `form`, `select`, `table`, `th`, `td`, `a`.
  - `templates/customer/order_detail.html` must include `h1`, `dl`, `dt`, `dd`, `a`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-filter-form`, `.data-table`, `.badge--ok`, `.customer-profile-dl`.
- Role/auth rules:
  - customer sees and tracks only own orders.
  - admin/staff can view broader order tracking lists.
- Data/validation rules:
  - status query filter must be supported on tracking lists.
  - detail access must enforce order ownership for customers.
- Layered boundaries:
  - route/controller: parse query params, enforce access, render pages.
  - service: apply role-scoped filtering and business rules.
  - repository: fetch order data by role/filter scope.
  - utils/db: shared DB helpers.
- Carry-forward requirements from Tasks 1-13:
  - preserve all previous API/auth/cart/order/inventory/workflow behavior and contracts.
  - keep Task 13 place-order workflow outcomes unchanged.
- Local run and verification steps:
  - log in as customer and open `/customer/orders`; verify status/details columns and filter form.
  - open one order detail and verify status/total fields.
  - attempt another customer’s order detail and confirm redirect back to `/customer/orders`.
  - log in as admin/staff and verify `/admin/orders?status=Placed` and `/staff/orders?status=Placed` pages.

## Objective of the task
Provide a role-aware, filterable order tracking experience across customer/admin/staff interfaces while enforcing secure order ownership checks.
