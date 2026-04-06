# 🛒 MarketHub — E-Commerce LLD (Low-Level Design)

## 📌 Overview

This document defines the **Low-Level Design (LLD)** for the MarketHub E-Commerce Web Application.

The system is built using a **Layered Monolith Architecture** to ensure:

* Clean code structure
* Scalability
* Maintainability
* Separation of concerns

---

# 🔹 Tech Stack

## 1. Python

* Core backend programming language
* Handles business logic and application flow

## 2. Flask

* Lightweight web framework
* Used to:

  * Create routes (APIs)
  * Handle requests & responses
  * Connect frontend with backend

---

## 3. Jinja2

* Template engine used with Flask
* Helps render dynamic HTML pages
* Used for:

  * Forms
  * Dashboards
  * Data display

---

## 4. MySQL

* Relational database
* Stores:

  * Users
  * Products
  * Categories
  * Orders
  * Cart

---

# 🔹 System Architecture

## Layered Monolith Architecture

```
Routes → Services → Repositories → Models → Database
```

---

## Layer Responsibilities

### 1. Routes Layer (`routes/`)

* Handles HTTP requests
* Calls services
* Returns responses

---

### 2. Services Layer (`services/`)

* Contains business logic
* Validates data
* Coordinates between layers

---

### 3. Repositories Layer (`repositories/`)

* Handles database queries
* No business logic

---

### 4. Models Layer (`models/`)

* Defines database schema
* Represents tables

---

### 5. Supporting Layers

| Layer      | Purpose                     |
| ---------- | --------------------------- |
| validators | Input validation            |
| exceptions | Custom error handling       |
| middleware | Request/response processing |
| config     | App & DB configuration      |
| utils      | Helper functions            |

---

# 🔹 User Roles

## 1. Admin

* Manages platform
* Controls users, categories, sellers

---

## 2. Seller (Store Staff)

* Manages products
* Handles inventory
* Processes orders

---

## 3. Customer

* Browses products
* Adds to cart
* Places orders

---

# 🔹 Core Modules

* User Management
* Category Management
* Product Management
* Cart System
* Order System
* Inventory Management

---

# 🔹 Use Case Flow

```
Customer → Browse Products → Add to Cart → Place Order → Track Order

Seller → Manage Products → View Orders → Update Status

Admin → Manage Users → Manage Categories → Monitor System
```

---

# 🔹 Tasks & Requirements

---

## 🔸 Task 1: Layered Project Structure Setup

### Goal:

Setup clean architecture

### Requirements:

* Create folders: routes, services, repositories, models
* Setup config module
* Initialize DB connection
* Setup dependency wiring
* Create standard API response

---

## 🔸 Task 2: Global Exception Handling & Logging

### Goal:

Centralized error management

### Requirements:

* BaseException class
* ValidationException
* NotFoundException
* AuthorizationException
* Global error handler
* Logging system
* Standard error response

---

## 🔸 Task 3: User Management

### Goal:

Handle authentication and roles

### Requirements:

* User model
* UserRepository
* UserService
* Registration & login
* Password hashing
* Role validation

---

## 🔸 Task 4: Base Layout & UI Validation

### Goal:

Reusable UI structure

### Requirements:

* base.html
* Navbar & footer
* Template inheritance
* Flash messages
* Form validation
* Error display

---

## 🔸 Task 5: Registration & Login UI

### Goal:

User interface for authentication

### Requirements:

* Registration form
* Login form
* Error handling
* Flash messages

---

## 🔸 Task 6: Admin Dashboard

### Goal:

Admin control panel

### Requirements:

* Admin home page
* Stats display
* Sidebar navigation
* Role-based UI

---

## 🔸 Task 7: Category & Store UI

### Goal:

Manage categories and staff

### Requirements:

* Create/edit categories
* Create/edit stores
* Assign staff
* Status toggle

---

## 🔸 Task 8: Product CRUD

### Goal:

Manage products

### Requirements:

* Product model
* ProductRepository
* ProductService
* Create, update, delete
* Validation

---

## 🔸 Task 9: Customer Dashboard

### Goal:

Product browsing interface

### Requirements:

* Profile display
* Category browsing
* Product listing
* Basic filtering

---

## 🔸 Task 10: Cart Management

### Goal:

Handle cart operations

### Requirements:

* Cart model
* CartRepository
* CartService
* Add/update/remove items
* Calculate totals

---

## 🔸 Task 11: Order Management

### Goal:

Handle order system

### Requirements:

* Order model
* OrderRepository
* OrderService
* Create order
* Status updates

---

## 🔸 Task 12: Inventory Management

### Goal:

Maintain stock consistency

### Requirements:

* Inventory model
* Deduct stock on order
* Prevent overselling
* Stock validation

---

## 🔸 Task 13: Order Placement Workflow

### Goal:

Combine cart, order, and inventory

### Requirements:

* Convert cart → order
* Lock inventory
* Clear cart
* Generate summary
* Transaction handling

---

## 🔸 Task 14: Order Tracking System

### Goal:

Track orders

### Requirements:

* View order history
* Filter orders
* Track status

---

## 🔸 Task 15: Order UI & Workflow Control

### Goal:

UI aligned with backend rules

### Requirements:

* Order details page
* Status display
* Filter by status
* Delivery tracking

---

# 🔹 Key Design Principles

## 1. SRP (Single Responsibility Principle)

Each layer has one responsibility

---

## 2. Separation of Concerns

* UI ≠ Business Logic ≠ DB

---

## 3. Scalability

* Easy to extend features

---

## 4. Maintainability

* Clean and modular code

---

## 5. Reusability

* Services and validators reusable

---

# 🔹 Final Outcome

After completing all tasks:

* Fully functional E-commerce system
* Clean architecture implementation
* Real-world backend design
* Strong understanding of:

  * LLD concepts
  * Service layer design
  * Transaction handling
  * Role-based access

---

# 🚀 Conclusion

This project transitions from:

* Basic CRUD → Structured System Design

It prepares you for:

* Backend development roles
* System design interviews
* Building scalable applications

---
