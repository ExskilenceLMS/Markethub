# Task 9: Customer dashboard

## Overview

Signed-in **customers** get a small **Shop** area under `/customer`: account profile, a read-only **category** list, and a read-only **product** catalog with optional category filter. There are no create, update, or delete actions in this flow.

## Read-only access

- Blueprint `customer_bp` uses `before_request` to allow only `role == customer`; others are redirected to login with a flash message.
- Templates show catalog data only (no edit/delete buttons, no POST forms except navigation).
- Product and category mutations remain on admin/staff routes only.

## Data flow (route → service → repository)

| Page | Route | Service | Repository (via service) |
|------|--------|-----------|---------------------------|
| Dashboard | `GET /customer/` | `UserService.get_user_by_id` | `UserRepository` |
| Categories | `GET /customer/categories` | `CategoryService.list_all_dicts` | `CategoryRepository` |
| Products | `GET /customer/products` | `CategoryService.list_all_dicts` (filter dropdown), `ProductService.list_catalog_dicts` | `CategoryRepository`, `ProductRepository` |

`ProductService.list_catalog_dicts(category_id=None)` loads either all products (`list_all_ordered`) or, when `category_id` is set, validates the category exists then loads `list_by_category_id`. Invalid category ids raise `ValidationException`; the route catches that, flashes, and falls back to the full list.

## Product and category viewing logic

- **Categories:** Sorted list from `CategoryRepository.list_all_ordered` (exposed as dicts). Each tile links to `products` with `?category_id=<id>`.
- **Products:** Dicts from `Product.to_dict()` (name, description, price, quantity, category name, image URL, etc.). Filter uses a GET select; changing the dropdown submits the form (with noscript fallback button).

## Files

- Routes: `routes/customer_routes.py`
- Services: `services/user_service.py`, `services/category_service.py`, `services/product_service.py`
- Repository addition: `ProductRepository.list_by_category_id`
- Templates: `templates/customer/dashboard.html`, `categories.html`, `products.html`
- Seed note: `database/seed_data.sql` (header comment; data already includes categories and sample products)
