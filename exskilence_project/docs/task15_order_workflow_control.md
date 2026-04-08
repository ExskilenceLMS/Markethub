# Task 15: Order UI & workflow control

## Order workflow control overview

Order placement and status tracking now align between UI and backend rules:

- customers place orders from cart and only view their own order history/details
- staff/admin can view all orders
- staff/admin can update order status only through valid workflow transitions
- status reversion is blocked by validation and reflected in UI controls

## Role-based access

- **Customer**
  - place order from cart (`POST /customer/orders/place`)
  - view own order list/details
  - no status update actions
- **Staff**
  - view all orders
  - update order status
- **Admin**
  - full visibility across all orders
  - update order status

## Status transition rules

Valid status transitions remain:

- `Placed` -> `Shipped`, `Cancelled`
- `Shipped` -> `Delivered`, `Cancelled`
- `Delivered` -> terminal
- `Cancelled` -> terminal

Backward/revert transitions are rejected by service validation (`assert_valid_status_transition`).

## UI workflow enforcement

- Order detail update dropdown (staff/admin) shows all status types used in filters, but non-allowed transitions are disabled.
- If an order is in a terminal state, status selector and save action are disabled.
- This keeps UI consistent with backend non-revert workflow rules.

## Restrictions after order placement

- Place-order workflow creates order, deducts stock, and clears cart in one transactional flow.
- Because cart rows are cleared on success, the placed cart is no longer modifiable.

