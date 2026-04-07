# Task 5: Registration & Login UI

Browser flows use **`routes/web_routes.py`**. JSON clients keep using **`routes/auth_routes.py`** (`/api/auth/...`).

## Registration and login flow

1. **GET** `/register` or `/login` renders a Jinja template extending **`base.html`** (no business logic in the template).
2. **POST** submits `application/x-www-form-urlencoded` data to the same route.
3. The route builds a **`dict`** and calls **`UserService.register`** or **`UserService.login`**.
4. On success: **`set_user_session`**, **`flash`** (success), **redirect** to the role home (**admin → `/admin`**, **seller → `/staff`**, **customer → `/customer`**).
5. On **`ValidationException`**: re-render the same page with **`form_errors`** (no redirect), using **`utils/form_errors.validation_exception_to_field_errors`** and **`templates/partials/form_errors.html`** macros—this is how “invalid login” and field errors are shown. **`flash`** is used for **success** after redirect.

Registration sends **`confirm_password`**; the validator checks a match when `confirm_password` is present (omitted by the JSON API so existing API behaviour stays the same). **Role** dropdown includes admin/seller/customer; the service still allows **self-registration only for customer**—other choices return a **`role`** field error.

## How the UI connects to backend services

| Layer | Responsibility |
| ----- | ---------------- |
| Template | Layout, fields, links, display of `form_errors` and flashed messages only. |
| Route | Read `request.form`, call service, set session / flash / redirect or render with errors. |
| **UserService** | Validation (via **validators**), hashing, persistence via **UserRepository**. |

No client-side validation logic is used beyond **`novalidate`** so the server remains authoritative.

## How validation errors are shown

- **`ValidationException.message`** and **`details`** (field names or structured hints) are normalized to a **`form_errors`** map.
- **`form_error_summary`** renders **`_form`** (non-field / general messages, e.g. invalid login).
- **`field_errors`** lists messages under the matching input and applies a **`user-error`** border class.

## Consistent UI (Flipkart-style)

**`static/css/style.css`** layers on **`base.css`**: primary blue **`#2874F0`**, light gray background **`#f1f3f6`**, white cards, blue header bar, full-width primary button on auth screens. Shared variables keep admin/staff/customer pages visually aligned with auth.

## Assets

- **`templates/auth/login.html`**, **`register.html`** — centered **`auth-page`** / **`auth-card`** layout.
- **`static/css/style.css`** — theme overrides.
