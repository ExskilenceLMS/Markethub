# Task 10: Cart management

## Overview

Each **customer** has a **persistent cart** stored in MySQL (`cart_items`): one row per user and product (unique pair), with a quantity. Customers add lines from the product catalog, update quantities, remove lines, or clear the cart. Totals are computed in the service layer from product prices.

## Persistent cart

- Cart rows survive logout and login (`user_id` ties lines to the account).
- Adding the same product again **merges** into the existing row (quantities sum).
- Removing a product or clearing the cart deletes rows; no session-only cart.

## Cart operations flow

| Operation | Route (customer) | Service | Repository |
|-----------|------------------|---------|------------|
| View summary | `GET /customer/cart` | `CartService.get_cart_summary` | `list_by_user_id` |
| Add | `POST /customer/cart/add` | `CartService.add` | `add_item` (merge) |
| Update qty | `POST /customer/cart/<line_id>/update` | `CartService.update_line` | `update_quantity` |
| Remove line | `POST /customer/cart/<line_id>/remove` | `CartService.remove_line` | `remove_item` |
| Clear | `POST /customer/cart/clear` | `CartService.clear` | `clear_for_user` |

Routes only parse `request.form`, call services, flash, and redirect (or render the cart page). **No** SQL, **no** business rules, **no** inline validation in routes.

## Validation rules

| Rule | Where |
|------|--------|
| `quantity` integer and **> 0** (add / update) | `validators/cart_validator.py` |
| `product_id` present and **> 0** (add) | `validators/cart_validator.py` |
| Product exists in DB | `CartService.add` via `ProductRepository.get_by_id` → `ValidationException` |
| Cart line belongs to current user | `CartRepository.get_by_id_for_user` → `NotFoundException` if missing |

Stock limits are **not** enforced in this task (only existence and positive quantity).

## Model and schema

- Model: `models/cart_item.py` (`CartItem`), table `cart_items`.
- DDL: `database/schema.sql` (FKs to `users`, `products`, `ON DELETE CASCADE`).
- Seed sample lines: `database/seed_data.sql` (Alice + two seed products).

## Related UI

- `templates/customer/cart.html` — line table, subtotals, grand total, clear/remove/update.
- `templates/customer/products.html` — “Add to cart” POST with `product_id`, `quantity`, optional `redirect_category_id`.
