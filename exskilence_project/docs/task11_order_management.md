# Task 11: Order management

## Overview

Orders record a **customer** (`user_id`), **total amount**, **status**, and timestamp. Customers **place orders** from the DB-backed cart (one atomic transaction: create order, reduce product stock, clear cart lines). **Admin** and **staff (seller)** can list all orders and move statuses through an allowed lifecycle. Customers see only their own orders.

## Persistent orders

- Rows live in `orders` (see `database/schema.sql`, `models/order.py`).
- Totals use `DECIMAL(12,2)`; status is a short string matching the values below.

## Order lifecycle (status flow)

| Status     | May transition to      |
|-----------|-------------------------|
| Placed    | Shipped, Cancelled      |
| Shipped   | Delivered, Cancelled    |
| Delivered | _(terminal)_            |
| Cancelled | _(terminal)_            |

Rules are enforced in `validators/order_validator.py` (`assert_valid_status_transition`, `next_status_choices` for UI).

## Role-based access

| Action              | Customer | Admin | Seller |
|---------------------|----------|-------|--------|
| Place order (cart)  | Yes      | No    | No     |
| List orders         | Own only | All   | All    |
| View order detail   | Own only | Any   | Any    |
| Update status       | No       | Yes   | Yes    |

`OrderService.get_dict` raises `AuthorizationException` if a customer requests another user’s order.

## Validation rules

| Rule | Enforcement |
|------|-------------|
| User exists (place order) | `UserRepository.get_by_id` in `OrderService.place_from_cart` |
| Cart not empty | `OrderService.place_from_cart` |
| Sufficient stock | Each cart line: `product.quantity >= line.quantity` before commit |
| Order exists (status update) | `OrderRepository.get_by_id` → `NotFoundException` |
| Valid status value | `parse_order_status_update` |
| Valid transition | `assert_valid_status_transition` |
| Only admin/seller update status | `OrderService.update_status` |

## Data flow (concise)

- **Place:** `POST /customer/orders/place` → `OrderService.place_from_cart` → `OrderRepository.create_from_cart_lines` (single DB transaction).
- **List:** `OrderService.list_dicts_for_role` → `OrderRepository.list_by_user_id` or `list_all_ordered`.
- **Status:** `POST .../orders/<id>` (admin/staff) → `OrderService.update_status` → `OrderRepository.update_status`.

## Files

- Model: `models/order.py`
- Repository: `repositories/order_repository.py`
- Validator: `validators/order_validator.py`
- Service: `services/order_service.py`
- Routes: `routes/customer_routes.py`, `routes/admin_routes.py`, `routes/staff_routes.py`
- UI: `templates/admin/order_list.html`, `order_detail.html`; `staff/order_list.html`, `order_detail.html`; `customer/orders.html`, `order_detail.html`; cart “Place order” in `customer/cart.html`
