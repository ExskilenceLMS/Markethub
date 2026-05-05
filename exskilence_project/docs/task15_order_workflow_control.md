# Task 15: Order UI & Workflow Control

## What is the task?
Finalize role-based order workflow control so admin/staff can update order status through guarded transitions, while customers remain read-only for status changes.

## Task requirements
- Access control behavior:
  - guests cannot open admin order detail pages (redirect to login).
  - customers cannot post status updates to admin/staff order routes; must be redirected to login pages.
- Admin order detail workflow UI:
  - `GET /admin/orders/<id>` must render status workflow controls with:
    - text `Update status`
    - `select id="status" name="status"`
    - `Save` submit action
  - template `templates/admin/order_detail.html` must include `h1`, `dl`, `dt`, `dd`, `form`, `select`, `button` and hooks `form-card`, `customer-profile-dl`, `btn-primary-fk`.
- Staff order detail workflow UI:
  - `templates/staff/order_detail.html` must include `h1`, `dl`, `form`, `select`, `button`, `label` and hooks `staff-hub`, `form-card`, `customer-profile-dl`.
- Status transition behavior:
  - admin can perform valid transition `Placed -> Shipped`.
  - staff invalid transition `Placed -> Delivered` must be blocked and order status must remain unchanged.
- Admin/staff order list filter UI:
  - `GET /admin/orders?status=Placed` and `GET /staff/orders?status=Placed` must render filter controls.
  - both pages must include `Filter by status` and `customer-filter-form`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.form-card`, `.badge--ok`, `.customer-profile-dl`, `.customer-filter-form`.
- Role/auth rules:
  - customer: no status update permission on admin/staff routes.
  - admin/staff: status workflow controls available per role routes.
- Data/validation rules:
  - status updates must follow allowed transition rules.
  - invalid transitions must not persist state changes.
- Layered boundaries:
  - route/controller: enforce access and request routing.
  - service: transition validation and workflow business rules.
  - repository: order retrieval and status persistence only.
  - utils/db: shared DB helpers.
- Carry-forward requirements from Tasks 1-14:
  - preserve all existing health/auth/error/cart/inventory/order/tracking behaviors and contracts.
  - keep customer order ownership checks and filter behavior from Task 14.
  - keep checkout stock deduction and oversell protections from Tasks 12-13.
- Local run and verification steps:
  - as admin, open order detail and verify status select + save controls.
  - post valid transition (`Placed` to `Shipped`) and verify persisted status.
  - as staff, attempt invalid transition (`Placed` to `Delivered`) and verify status unchanged.
  - as customer, attempt admin/staff status update POST and verify access is blocked.

## Objective of the task
Complete a secure, role-driven order workflow interface where status control is available only to authorized roles and enforced by strict transition rules without breaking earlier order features.

