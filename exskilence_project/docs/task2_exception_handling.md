# Task 2: Global Exception Handling & Logging

This document aligns with the MarketHub layered monolith described in `docs/e_commerce.md` (LLD).

## Why centralized exception handling

Without a single place to translate exceptions into HTTP responses, every route would need `try/except`, responses would drift in shape, and stack traces or database messages could leak to clients. Central handlers keep **routes thin**, enforce one **JSON contract**, and let **services and repositories** signal failures by raising typed exceptions.

## Types of exceptions

| Type | Module | Typical HTTP status | When to use |
| ---- | ------ | ------------------- | ----------- |
| `ApplicationBaseException` | `exceptions/base_exception.py` | Configurable (default 400) | Base for all application-defined errors; carries `message`, `status_code`, and `details`. |
| `ValidationException` | `exceptions/validation_exception.py` | 400 | Invalid input or failed business validation. |
| `NotFoundException` | `exceptions/not_found_exception.py` | 404 | Missing entity or resource. |
| `AuthorizationException` | `exceptions/authorization_exception.py` | 403 | Permission or authorization failure. |

The class is named `ApplicationBaseException` (not Python’s built-in `BaseException`) to avoid confusion and unsafe shadowing.

## Business errors vs system errors

- **Business errors** are expected failure paths: validation, not found, forbidden. They inherit from `ApplicationBaseException`, return a stable **structured JSON** body (no raw SQL or stack traces), and are usually logged at **WARNING** (or **ERROR** for 5xx-class business codes if you choose to use them).
- **System errors** are unexpected bugs, infrastructure faults, or unhandled exceptions. The global handler logs the full exception at **ERROR** with traceback and returns a **generic** message to the client so internal details are not exposed. In **debug** mode, unexpected exceptions are re-raised so Flask’s debugger can run.

Werkzeug **`HTTPException`** (e.g. `abort(404)`) is handled separately so framework-level HTTP errors still use the same JSON envelope.

## Logging: importance and levels

| Level | Use |
| ----- | --- |
| **INFO** | Normal lifecycle events (e.g. application startup). |
| **WARNING** | Recoverable or expected problems (4xx-style HTTP issues, business errors you want in logs). |
| **ERROR** | Failures that need attention (5xx, unhandled exceptions, upstream failures). |

Configuration lives in `config/logging_config.py`. Root logging is attached to **stdout** with a consistent format. Verbosity is controlled with **`LOG_LEVEL`** (default `INFO`). Werkzeug request logs are capped at **WARNING** to reduce noise.

## Standard API envelopes

Implemented in `utils/response.py` and used by handlers and routes.

**Success:**

```json
{
  "success": true,
  "data": {},
  "message": "optional"
}
```

`message` is omitted when not passed to `success_response`.

**Error:**

```json
{
  "success": false,
  "error": {
    "message": "",
    "details": []
  }
}
```

## Where things are wired

- **Handlers:** `middleware/error_handlers.py` — `ApplicationBaseException`, `HTTPException`, then catch-all `Exception` (generic 500 when not in debug).
- **App startup:** `app.py` calls `setup_logging()` and logs an **INFO** line when the app is ready.
- **Routes:** should not wrap business logic in `try/except`; raise domain exceptions from services/repositories instead.
