# Task 14: Order tracking system

## Overview

Order tracking is available across roles with lifecycle visibility:

- customers can view only their own orders and status
- staff/admin can view all orders and update status
- all order list pages support filtering by status

## Role-based access

- **Customer**
  - `GET /customer/orders`: own order history (view only)
  - `GET /customer/orders/<id>`: own order detail (view only)
- **Staff**
  - `GET /staff/orders`: all orders
  - `GET/POST /staff/orders/<id>`: view and update status
- **Admin**
  - `GET /admin/orders`: all orders
  - `GET/POST /admin/orders/<id>`: view and update status

## Status flow

Statuses:

- `Placed`
- `Shipped`
- `Delivered`
- `Cancelled`

Valid transitions are enforced by order validation logic:

- `Placed` -> `Shipped` or `Cancelled`
- `Shipped` -> `Delivered` or `Cancelled`
- `Delivered` -> terminal
- `Cancelled` -> terminal

## Filtering logic

- Query parameter: `status`
- Status filter is applied in service layer (`OrderService.list_dicts_for_role_filtered`)
- Invalid status values raise validation error and list falls back to unfiltered result
- Filtering behavior respects role scope:
  - customer: only own orders for selected status
  - staff/admin: all orders for selected status

## Validation

- Order must exist before detail/status update
- Status update must be valid and follow allowed transitions
- Invalid filter/status inputs are rejected by service/validator logic
