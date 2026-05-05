# Task 10: Cart Management

## What is the task?
Implement customer cart workflows for add, view, update quantity, and clear actions with correct redirects, totals, and UI hooks.

## Task requirements
- Route/auth behavior:
  - `GET /customer/cart` must redirect guests to login.
  - logged-in customer can access `GET /customer/cart` with HTTP `200`.
- Cart page requirements (`templates/customer/cart.html`):
  - render `customer-hub`, `customer-cart-card`, and `customer-cart__total` hooks.
  - include cart title/content (`Cart`).
  - when empty, show `Your cart is empty`.
  - include line table/update form controls when cart has items.
- Add-to-cart behavior:
  - `POST /customer/cart/add` must redirect (HTTP `302`) to `/customer/products`.
  - adding same `product_id` multiple times must merge into one cart line by increasing quantity.
  - cart total must reflect merged quantity calculation.
- Update/clear behavior:
  - `POST /customer/cart/<line_id>/update` must update quantity and refresh rendered total.
  - `POST /customer/cart/clear` must remove all lines and show empty-state message.
- Products page add-to-cart form requirements (`templates/customer/products.html`):
  - each product card must include add-to-cart form posting `product_id` and `quantity`.
  - include hooks `customer-product-card__cart-form` and `customer-cart__qty-input`.
- HTML structure requirements:
  - `templates/customer/cart.html` must include `header`, `h1`, `form`, `table`, `th`, `td`, `button` plus required identifiers.
  - `templates/customer/products.html` must include `form`, `input`, `button`, `label`, `ul`, `li` with required identifiers above.
- CSS requirements (`static/css/style.css`):
  - include selectors `.customer-cart-card`, `.customer-product-card__cart-form`, `.customer-cart__total`, `.customer-cart__qty-input`.
- Role/auth rules:
  - only authenticated customers can perform cart actions.
- Data/validation rules:
  - add/update quantities must be positive.
  - add must target valid product.
- Layered boundaries:
  - route/controller: read form data, call service, redirect/render.
  - service: cart business rules (merge, totals, validation orchestration).
  - repository: cart row persistence/query only.
  - utils/db: shared DB/session support.
- Carry-forward requirements from Tasks 1-9:
  - preserve previous API contracts, auth flows, admin/staff/product features, and customer dashboard/catalog behavior.
- Local run and verification steps:
  - as customer, open `/customer/cart` and verify empty state.
  - add a product from `/customer/products` and verify redirect to products and cart totals.
  - add same product twice and confirm merged quantity.
  - update line quantity and clear cart; verify total/empty state updates.

## Objective of the task
Deliver a reliable customer cart experience with stable quantity and total behavior, clear UI structure, and strict customer-only access without breaking earlier flows.
