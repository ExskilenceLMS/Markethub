# Task 13: Order placement workflow

## Workflow steps

Order placement now follows an explicit orchestration path:

1. Fetch cart summary and cart rows
2. Validate user existence
3. Validate stock availability for each cart item
4. Create order record
5. Deduct product stock
6. Clear cart rows

Steps 4-6 execute in a single transaction through repository logic.

## Service orchestration

`services/order_workflow_service.py` coordinates:

- `CartService` for cart summary calculation
- `InventoryService` for stock validation
- `OrderService` for user validation and finalized order creation

This keeps route handlers thin and centralizes order-placement flow in service layer orchestration.

## Transaction consistency

`OrderRepository.create_from_cart_lines(...)` performs order creation, stock deduction, and cart cleanup in one commit.
If any part fails, transaction rollback keeps cart, inventory, and order data consistent.

## Validation rules applied

- Cart must not be empty
- User must exist
- Product must exist for every cart line
- Requested quantity must be greater than zero
- Requested quantity must be less than or equal to available product stock

## Files updated for this task

- `services/order_workflow_service.py`
- `services/order_service.py`
- `routes/customer_routes.py`
- `database/seed_data.sql`
