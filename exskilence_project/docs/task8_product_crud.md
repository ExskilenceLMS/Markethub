# Task 8: Product CRUD

## Overview

Products are catalog rows tied to a **category** and a **seller**. Admins manage the full catalog and assign any seller; sellers manage **only their own** products. Create, read, update, and delete are exposed via **admin** and **staff** routes; validation and access rules live outside the route handlers.

## Layer responsibilities

| Layer | Responsibility |
|--------|----------------|
| **Routes** (`routes/admin_routes.py`, `routes/staff_routes.py`) | HTTP only: session role checks (via blueprint `before_request`), parse `request.form`, call services, flash and redirect or render templates. No SQL, no business rules, no field validation logic. |
| **Services** (`services/product_service.py`) | List scope by role, load product, create/update/delete orchestration, category existence, seller role check (admin path), ownership for seller updates/deletes. |
| **Repositories** (`repositories/product_repository.py`) | Persistence: create (with flush for id), get by id (eager category/seller), list all / by seller, update, delete. |
| **Models** (`models/product.py`) | SQLAlchemy mapping and `to_dict()` for API-shaped dicts (including `category_name`, `seller_name`). |
| **Validators** (`validators/product_validator.py`) | Parse and validate payload: required name, price &gt; 0, quantity ≥ 0, category id present, optional description/image; `seller_id` required when acting as admin. |

## Validation approach

- **Field rules** are enforced in `parse_product_payload`: missing/invalid values raise `ValidationException` with `details` for field keys; routes map these to template `form_errors` via `validation_exception_to_field_errors`.
- **Referential rules** (`category` exists, `seller` is a user with role `seller`) are enforced in `ProductService` after parsing.
- **HTML5** attributes on forms are for UX only; authoritative checks remain server-side.

## Role-based access

| Role | List | Create | Update | Delete |
|------|------|--------|--------|--------|
| **admin** | All products | Yes; must pick a seller | Yes; can change seller | Yes; any product |
| **seller** | Own products only | Yes; `seller_id` is session user | Own products only | Own products only |
| **customer** | Not used in these UIs | N/A | N/A | N/A |

Ownership is enforced in `ProductService._can_modify` and in staff `product_edit` GET (early redirect if `product.seller_id != uid`).

## Related files

- Schema: `database/schema.sql` (`products` table).
- Seed: `database/seed_data.sql` (second seller, store–category links, sample products).
- Admin UI: `templates/admin/product_list.html`, `templates/admin/product_form.html`.
- Staff UI: `templates/staff/product_list.html`, `templates/staff/product_form.html`.
