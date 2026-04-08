-- MarketHub dummy data (MySQL 8+)
-- Run after schema.sql against the same database as the app (e.g. markethub).
-- All seeded users share password (local dev only): user123
-- Categories / stores use seller@example.com as owner (must exist from user seed).
-- Task 9 (customer dashboard): categories below + sample products later in this file support read-only browse.
-- Task 10 (cart): sample cart lines for alice@example.com after products are inserted.
-- Task 11 (orders): sample orders below (users + products must exist).
-- Task 12 (inventory): product quantities seeded below are used for stock validation and deduction.
-- Task 13 (order workflow): users/products/cart seed data below supports end-to-end placement flow.
-- Task 14 (order tracking): multiple order statuses are seeded for filter scenarios.
-- Task 15 (workflow control): status mix below supports UI transition control and non-revert rules.

SET NAMES utf8mb4;

INSERT INTO users (name, email, password_hash, role, created_at) VALUES
(
    'System Admin',
    'admin@example.com',
    'pbkdf2:sha256:260000$j9Z87dVajVZKf7nU$457f4123677d19acae106e2e326450ff991823005e95ff9d1b5d44f1f2cbec8e',
    'admin',
    '2026-01-15 10:00:00'
),
(
    'Store Seller',
    'seller@example.com',
    'pbkdf2:sha256:260000$j9Z87dVajVZKf7nU$457f4123677d19acae106e2e326450ff991823005e95ff9d1b5d44f1f2cbec8e',
    'seller',
    '2026-01-15 10:05:00'
),
(
    'Alice Customer',
    'alice@example.com',
    'pbkdf2:sha256:260000$j9Z87dVajVZKf7nU$457f4123677d19acae106e2e326450ff991823005e95ff9d1b5d44f1f2cbec8e',
    'customer',
    '2026-01-16 09:00:00'
),
(
    'Bob Customer',
    'bob@example.com',
    'pbkdf2:sha256:260000$j9Z87dVajVZKf7nU$457f4123677d19acae106e2e326450ff991823005e95ff9d1b5d44f1f2cbec8e',
    'customer',
    '2026-01-16 09:30:00'
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    password_hash = VALUES(password_hash),
    role = VALUES(role);

-- Categories (unique name)
INSERT INTO categories (name, description, created_at) VALUES
('Electronics', 'Phones, laptops, accessories', '2026-01-18 10:00:00'),
('Fashion', 'Clothing, footwear, and accessories', '2026-01-18 10:00:00'),
('Home & Kitchen', 'Furniture, appliances, cookware', '2026-01-18 10:00:00'),
('Books', 'Fiction, non-fiction, and study guides', '2026-01-18 10:00:00'),
('Sports & Fitness', 'Equipment, apparel, outdoor gear', '2026-01-18 10:00:00')
ON DUPLICATE KEY UPDATE
    description = VALUES(description);

-- Stores (seller resolved by email; skip if store name already exists)
INSERT INTO stores (name, seller_id, is_active, created_at)
SELECT 'TechHub Outlet', u.id, 1, '2026-01-20 11:00:00'
FROM users u
WHERE u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.name = 'TechHub Outlet')
LIMIT 1;

INSERT INTO stores (name, seller_id, is_active, created_at)
SELECT 'Fashion Corner', u.id, 0, '2026-01-20 12:00:00'
FROM users u
WHERE u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.name = 'Fashion Corner')
LIMIT 1;

INSERT INTO stores (name, seller_id, is_active, created_at)
SELECT 'Sports Zone', u.id, 1, '2026-01-21 09:00:00'
FROM users u
WHERE u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.name = 'Sports Zone')
LIMIT 1;

-- Store ↔ category links (INSERT IGNORE = safe if re-run)
INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Electronics'
WHERE s.name = 'TechHub Outlet';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Home & Kitchen'
WHERE s.name = 'TechHub Outlet';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Books'
WHERE s.name = 'TechHub Outlet';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Fashion'
WHERE s.name = 'Fashion Corner';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Sports & Fitness'
WHERE s.name = 'Sports Zone';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Electronics'
WHERE s.name = 'Sports Zone';

-- Second seller (same dev password: user123)
INSERT INTO users (name, email, password_hash, role, created_at) VALUES
(
    'Second Seller',
    'seller2@example.com',
    'pbkdf2:sha256:260000$j9Z87dVajVZKf7nU$457f4123677d19acae106e2e326450ff991823005e95ff9d1b5d44f1f2cbec8e',
    'seller',
    '2026-01-17 10:00:00'
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    password_hash = VALUES(password_hash),
    role = VALUES(role);

INSERT INTO stores (name, seller_id, is_active, created_at)
SELECT 'Urban Wear Co.', u.id, 1, '2026-01-22 10:00:00'
FROM users u
WHERE u.email = 'seller2@example.com'
  AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.name = 'Urban Wear Co.')
LIMIT 1;

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Fashion'
WHERE s.name = 'Urban Wear Co.';

INSERT IGNORE INTO store_categories (store_id, category_id)
SELECT s.id, c.id
FROM stores s
INNER JOIN categories c ON c.name = 'Books'
WHERE s.name = 'Urban Wear Co.';

-- Sample products (idempotent by product name)
INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed USB-C Cable 2m', 'Braided charging cable', 299.00, 120,
    c.id, u.id, NULL, '2026-01-25 10:00:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Electronics' AND u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed USB-C Cable 2m')
LIMIT 1;

INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed Python Basics Guide', 'Introductory programming text', 449.00, 40,
    c.id, u.id, NULL, '2026-01-25 10:05:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Books' AND u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed Python Basics Guide')
LIMIT 1;

INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed Stainless Kettle 1.5L', 'Electric kettle with auto shut-off', 1299.00, 25,
    c.id, u.id, NULL, '2026-01-25 10:10:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Home & Kitchen' AND u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed Stainless Kettle 1.5L')
LIMIT 1;

INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed Yoga Mat 6mm', 'Non-slip exercise mat', 799.00, 60,
    c.id, u.id, NULL, '2026-01-25 10:15:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Sports & Fitness' AND u.email = 'seller@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed Yoga Mat 6mm')
LIMIT 1;

INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed Cotton Crew Tee', 'Regular fit, pre-shrunk cotton', 499.00, 200,
    c.id, u.id, NULL, '2026-01-25 11:00:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Fashion' AND u.email = 'seller2@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed Cotton Crew Tee')
LIMIT 1;

INSERT INTO products (name, description, price, quantity, category_id, seller_id, image_url, created_at)
SELECT 'Seed Fiction Anthology Vol 1', 'Short stories collection', 349.00, 80,
    c.id, u.id, NULL, '2026-01-25 11:05:00'
FROM categories c
CROSS JOIN users u
WHERE c.name = 'Books' AND u.email = 'seller2@example.com'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.name = 'Seed Fiction Anthology Vol 1')
LIMIT 1;

-- Sample cart (persistent DB cart) for customer alice@example.com
INSERT INTO cart_items (user_id, product_id, quantity, created_at)
SELECT u.id, p.id, 2, '2026-01-26 10:00:00'
FROM users u
INNER JOIN products p ON p.name = 'Seed USB-C Cable 2m'
WHERE u.email = 'alice@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM cart_items c WHERE c.user_id = u.id AND c.product_id = p.id
  )
LIMIT 1;

INSERT INTO cart_items (user_id, product_id, quantity, created_at)
SELECT u.id, p.id, 1, '2026-01-26 10:05:00'
FROM users u
INNER JOIN products p ON p.name = 'Seed Python Basics Guide'
WHERE u.email = 'alice@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM cart_items c WHERE c.user_id = u.id AND c.product_id = p.id
  )
LIMIT 1;

INSERT INTO cart_items (user_id, product_id, quantity, created_at)
SELECT u.id, p.id, 1, '2026-01-26 10:10:00'
FROM users u
INNER JOIN products p ON p.name = 'Seed Yoga Mat 6mm'
WHERE u.email = 'bob@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM cart_items c WHERE c.user_id = u.id AND c.product_id = p.id
  )
LIMIT 1;

-- Sample orders (historical; independent of current cart)
INSERT INTO orders (user_id, total_amount, status, created_at)
SELECT u.id, 1047.00, 'Placed', '2026-01-28 14:00:00'
FROM users u
WHERE u.email = 'bob@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount = 1047.00 AND o.status = 'Placed'
  )
LIMIT 1;

INSERT INTO orders (user_id, total_amount, status, created_at)
SELECT u.id, 349.00, 'Shipped', '2026-01-27 09:00:00'
FROM users u
WHERE u.email = 'alice@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount = 349.00 AND o.status = 'Shipped'
  )
LIMIT 1;

INSERT INTO orders (user_id, total_amount, status, created_at)
SELECT u.id, 799.00, 'Delivered', '2026-01-26 08:00:00'
FROM users u
WHERE u.email = 'alice@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount = 799.00 AND o.status = 'Delivered'
  )
LIMIT 1;

INSERT INTO orders (user_id, total_amount, status, created_at)
SELECT u.id, 499.00, 'Cancelled', '2026-01-25 16:30:00'
FROM users u
WHERE u.email = 'bob@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount = 499.00 AND o.status = 'Cancelled'
  )
LIMIT 1;
