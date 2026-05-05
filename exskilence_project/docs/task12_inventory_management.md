# Task 12: Inventory & Stock Management

## What is the task?
Implement inventory safeguards for cart and order workflows so stock is displayed clearly, invalid quantities are blocked, and overselling is prevented during order placement.

## Task requirements
- Cart/customer access behavior:
  - guest users cannot access `/customer/cart` and must be redirected to login.
- Stock deduction behavior:
  - placing order from cart must deduct product stock by ordered quantity.
  - placing order from cart must create order and clear cart on success.
- Oversell prevention behavior:
  - if requested cart quantity exceeds available stock, place-order must be blocked.
  - blocked place-order must redirect to `/customer/cart`.
  - when blocked, product stock must remain unchanged, no order should be created, and cart line should remain.
- Product quantity validation behavior:
  - product creation/update path must reject negative stock quantity values.
- Customer catalog/cart UI requirements:
  - products page must display stock text (`Stock:`), quantity input control, and `Add to cart` action.
  - cart page must include quantity update form, total row, and place-order action controls.
  - cart update with zero quantity must be rejected and existing line quantity must remain unchanged.
- HTML structure requirements:
  - `templates/customer/products.html` must include `ul`, `li`, `form`, `input`, `label`, `button`, `p` and hooks `customer-product-grid`, `customer-product-card__qty`, `customer-cart__qty-input`, `customer-product-card__cart-form`.
  - `templates/customer/cart.html` must include `table`, `form`, `input`, `button`, `p` and hooks `customer-cart__qty-form`, `customer-cart__total`, `customer-cart__place-row`.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-product-card__qty`, `.customer-cart__qty-input`, `.customer-cart__place-row`, `.customer-cart-card`.
- Role/auth rules:
  - only authenticated customers can perform cart and place-order actions.
- Data/validation rules:
  - quantity values for cart updates/orders must be positive.
  - inventory must be checked before reducing stock.
- Layered boundaries:
  - route/controller: redirects, form parsing, page rendering.
  - service: inventory/business validation and order orchestration.
  - repository: stock/cart/order persistence and transactional writes.
  - utils/db: shared DB/session handling.
- Carry-forward requirements from Tasks 1-11:
  - preserve all prior API contracts, auth behavior, cart/order flow, and admin/staff/customer UI behavior.
  - keep Task 11 order status and ownership controls unchanged.
- Local run and verification steps:
  - open `/customer/products` and verify stock label + quantity input appear.
  - add item to cart, place order, and verify redirect to `/customer/orders` with stock reduction.
  - test over-quantity scenario and confirm redirect to cart with no stock/order mutation.
  - test cart quantity update to `0` and confirm existing line quantity stays unchanged.

## Objective of the task
Guarantee accurate and safe inventory behavior across cart and checkout actions by enforcing stock constraints, preventing oversell, and keeping customer UI controls consistent.
