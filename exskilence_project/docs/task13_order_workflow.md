# Task 13: Order Placement Workflow

## What is the task?
Implement a robust customer cart-to-order workflow that consistently handles auth, validation, stock checks, and final order listing behavior.

## Task requirements
- Auth and route behavior:
  - guest `POST /customer/orders/place` must redirect to login.
  - authenticated customer cart checkout should flow through place-order route.
- Successful workflow behavior:
  - `POST /customer/orders/place` with valid cart must redirect to `/customer/orders`.
  - one order must be created with status `Placed`.
  - product stock must be reduced by cart quantities.
  - cart lines must be cleared after success.
- Failure workflow behavior:
  - empty cart place-order must redirect to `/customer/cart` and create no order.
  - oversell attempt (cart quantity > stock) must redirect to `/customer/cart`.
  - in oversell failure, no order should be created and cart lines must remain.
- Orders list behavior:
  - after successful workflow, `GET /customer/orders` must render with title `My orders`.
  - orders list must display order id marker (`#`) and status `Placed`.
- HTML requirements:
  - `templates/customer/cart.html` must include `table`, `form`, `button`, `input`, `p` with hooks `customer-cart-card`, `customer-cart__total`, `customer-cart__place-row`, `customer-cart__qty-form`.
  - `templates/customer/orders.html` must include `h1`, `table`, `th`, `td`, `a` with hooks `customer-hub`, `data-card`, `data-table`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-cart__place-row`, `.customer-cart__total`, `.customer-cart__qty-input`, `.customer-product-card__qty`.
- Role/auth rules:
  - only authenticated customers can place orders through customer workflow.
- Data/validation rules:
  - cart must not be empty.
  - requested quantity must be valid and within stock.
  - order creation, stock deduction, and cart cleanup must remain consistent as one workflow.
- Layered boundaries:
  - route/controller: receives request and redirects.
  - service: orchestrates checkout business steps.
  - repository: transactional persistence updates.
  - utils/db: transactional/session utilities.
- Carry-forward requirements from Tasks 1-12:
  - preserve all prior API/auth/cart/order/inventory/admin/staff/customer behavior and contracts.
  - keep Task 12 stock validation and zero/negative quantity protections unchanged.
- Local run and verification steps:
  - as customer, add product to cart and place order; confirm redirect to `/customer/orders` and `Placed` status shown.
  - test empty-cart place-order and verify redirect to `/customer/cart`.
  - test over-quantity place-order and verify cart remains with no new order.

## Objective of the task
Deliver a reliable end-to-end checkout workflow that safely converts cart items into orders while protecting data consistency and preserving all prior behavior.
