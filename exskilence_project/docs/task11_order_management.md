# Task 11: Order Management

## What is the task?
Implement order placement from customer cart, customer order history access control, and admin order status updates.

## Task requirements
- Customer orders access behavior:
  - guests requesting `GET /customer/orders` must be redirected to login.
  - logged-in customer can access `GET /customer/orders` and see order listing.
  - customer must not access another customer’s order detail (`/customer/orders/<id>`); redirect back to `/customer/orders`.
- Place-order behavior (`POST /customer/orders/place`):
  - with non-empty cart: create order, set initial status `Placed`, reduce product stock, clear cart lines, and redirect to `/customer/orders`.
  - with empty cart: do not create order; redirect to `/customer/cart`.
- Customer order listing page requirements (`templates/customer/orders.html`):
  - include heading such as `My orders`.
  - render order rows including order id and status (for example `Placed`).
  - include `customer-hub`, `data-card`, and `data-table` hooks.
- Admin order update behavior:
  - `POST /admin/orders/<id>` with `status=Shipped` must persist new status and redirect to `/admin/orders/<id>`.
- Admin order detail template requirements (`templates/admin/order_detail.html`):
  - include status/detail display with `h1`, `dl`, `dt`, `dd`.
  - include status update form with `select` and submit `button`.
  - include hooks `customer-profile-dl`, `form-card`, and `btn-primary-fk`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-profile-dl`, `.badge--ok`, `.customer-cart__place-row`, `.data-table`.
- Role/auth rules:
  - customers can place orders and see only their own orders.
  - admin can update order status.
- Data/validation rules:
  - order placement requires non-empty cart.
  - stock must be reduced when order is placed successfully.
  - order status updates must validate allowed status values/transitions.
- Layered boundaries:
  - route/controller: handle requests, redirects, rendering.
  - service: transactional order placement and authorization rules.
  - repository: order/cart/product persistence operations.
  - utils/db: shared transaction and DB utilities.
- Carry-forward requirements from Tasks 1-10:
  - preserve all prior health/auth/error/cart/product/admin/customer behavior unchanged.
  - keep cart add/update/clear behavior from Task 10 unchanged.
- Local run and verification steps:
  - as customer, add cart item and place order; confirm redirect to `/customer/orders` and `Placed` status appears.
  - attempt placing order with empty cart and confirm redirect to `/customer/cart`.
  - as different customer, open another order detail and confirm access is blocked.
  - as admin, update order to `Shipped` and verify persisted status.

## Objective of the task
Introduce a consistent order lifecycle starting from cart checkout, with strict ownership rules for customers and controlled status management for admin users.
