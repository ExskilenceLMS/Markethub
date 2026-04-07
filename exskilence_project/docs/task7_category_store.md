# Task 7: Category & Store UI (Structured Forms)

## Category and store management flow

1. **Admin** opens **Categories** or **Stores** from the admin sidebar (`/admin/categories`, `/admin/stores`).
2. **List** views load data prepared in **`CategoryService.list_all_dicts()`** and **`StoreService.list_all_dicts()`** (plain dicts for templates).
3. **Add / edit** forms POST to the same blueprint; **`routes/admin_routes.py`** builds a form dict (`request.form` / `getlist` for category checkboxes) and calls **`CategoryService.create/update`** or **`StoreService.create/update`**.
4. On success, **flash** + **redirect** to the list. On **`ValidationException`**, the route re-renders the form with **`form_errors`** from **`validation_exception_to_field_errors`** (same pattern as auth).

**Staff management** (`/admin/staff/manage`) shows each **seller** and their **stores** with **categories** and links to **edit store**—assignment changes happen through the **store form** (seller + category checkboxes).

## Role-based access (admin vs seller)

| Area | Admin | Seller |
| ---- | ----- | ------ |
| Create / edit / delete categories | Yes (`admin_bp` + `before_request`) | No |
| Create / edit / delete stores | Yes | No |
| View categories / stores | Yes | **Read-only** under **`/staff/categories`** and **`/staff/stores`** (`staff_bp` + seller `before_request`) |

Sellers only see categories that appear on **their** stores (`CategoryService.list_for_seller`) and only **their** stores (`StoreService.list_for_seller`). The top **Staff** link goes to **`staff.dashboard`**.

## Form validation (backend + UI)

- **Validators:** **`validators/category_validator.py`**, **`validators/store_validator.py`** parse and check required fields (name, seller, etc.).
- **Services** enforce rules: unique category name, seller must exist and have role **`seller`**, category IDs must exist.
- Templates use **`novalidate`**, **`form_error_summary`**, and **`field_errors`**; no business rules in Jinja.

## Relationships: store, seller, categories

- **`Store`** has **`seller_id`** → **`users.id`** (the assigned seller/staff user).
- **`Store`** ↔ **`Category`** is **many-to-many** via **`store_categories`** (`models/store.py`).
- A **seller** may run **multiple stores**; each store can list **multiple categories** for merchandising / reporting. Admins define both links; sellers **view** the result on staff pages.

## Files added or updated (reference)

- **Models:** `models/category.py`, `models/store.py` (+ `store_categories` table).
- **Repositories:** `repositories/category_repository.py`, `repositories/store_repository.py`; **`UserRepository.list_users_by_role`** for seller dropdown.
- **Services:** `services/category_service.py`, `services/store_service.py`; **`AdminService`** stats include category/store counts.
- **Routes:** `routes/admin_routes.py` (CRUD + staff overview), **`routes/staff_routes.py`** (read-only seller views); **`web_routes`** no longer defines `/staff`.
- **Templates:** `admin/category_list.html`, `category_form.html`, `store_list.html`, `store_form.html`, `staff_management.html`; staff: `category_readonly.html`, `store_readonly.html`; updated **`staff/dashboard.html`**, **`partials/admin_sidebar.html`**.
- **Schema:** `database/schema.sql` — `categories`, `stores`, `store_categories`.

## Consistent UI

**`static/css/style.css`** adds **data tables**, **form cards**, **badges**, **staff hub** cards, and aligns with the Flipkart-style primary blue already used on auth and admin shells.
