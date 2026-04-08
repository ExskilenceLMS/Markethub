# Task 12: Inventory & stock management

## Inventory overview

Inventory is managed using `products.quantity` as the source of truth. During order placement, cart quantities are validated against current stock and product stock is deducted in the same order transaction.

## Stock validation logic

- `services/inventory_service.py` introduces `InventoryService`.
- `InventoryService.ensure_cart_items_have_stock(cart_rows)` checks:
  - cart is not empty
  - each referenced product exists
  - each requested quantity is valid (`> 0`)
  - requested quantity does not exceed available stock
- `validators/inventory_validator.py` contains quantity validation for inventory checks.

## Overselling prevention

- Pre-check: `OrderService.place_from_cart` now delegates stock validation to `InventoryService`.
- Transaction-time guard: `OrderRepository.create_from_cart_lines` re-checks stock before decrementing in the same DB transaction.
- If stock is insufficient at either step, a `ValidationException` is raised and order placement is blocked.

## Interaction with order system

- `OrderService.place_from_cart` flow:
  1. validate user exists
  2. read cart rows and total
  3. validate inventory via `InventoryService`
  4. call `OrderRepository.create_from_cart_lines`
- `OrderRepository.create_from_cart_lines` performs:
  - create order
  - deduct stock (`products.quantity -= cart.quantity`)
  - clear cart rows
  - commit

This keeps inventory and order placement consistent and prevents overselling for cart-based orders.
