-- =============================================================
-- Sales Manager – Sample Seed Data
-- Run after 01_create_tables.sql:
--   psql -U postgres -d sales_manager -f 02_seed_data.sql
-- =============================================================

-- Products
INSERT INTO products (code, category, description, color, cost, comments) VALUES
    ('ONX-RND-BLK', 'Coasters',    'Onyx Round Coaster',          'Black',  3.50, NULL),
    ('ONX-SQR-GRN', 'Coasters',    'Onyx Square Coaster',         'Green',  3.75, NULL),
    ('MRB-ORN-WHT', 'Ornaments',   'Marble Ornament',             'White',  5.00, NULL),
    ('CHE-BOX-BRN', 'Boxes',       'Chess Storage Box',           'Brown', 12.00, 'Hinged lid'),
    ('CHE-BOX-BLK', 'Boxes',       'Chess Storage Box',           'Black', 12.00, 'Hinged lid')
ON CONFLICT (code) DO NOTHING;

-- Orders
INSERT INTO orders (order_no, order_date, qty, color, source, platform, order_amount, sales_tax, comments) VALUES
    ('3786172159', '2024-03-15', 2, 'Black', 'Suaz-3', 'Etsy', 35.00,  2.80, NULL),
    ('3784939393', '2024-03-10', 1, 'Green', 'Suaz-3', 'Etsy', 18.50,  1.48, NULL),
    ('3747658570', '2024-02-28', 3, 'White', 'Suaz-3', 'Etsy', 52.00,  4.16, NULL)
ON CONFLICT (order_no) DO NOTHING;

-- Shipment header
INSERT INTO shipment_header (supplier_name, shipment_no, date_received, comments) VALUES
    ('AliExpress Supplier A', 'SHIP-2024-001', '2024-01-20', 'First batch of coasters'),
    ('AliExpress Supplier B', 'SHIP-2024-002', '2024-02-10', 'Chess boxes and ornaments')
ON CONFLICT DO NOTHING;

-- Shipment products (referencing the two headers above by expected id 1 and 2)
INSERT INTO shipment_products (shipment_header_id, description, sku, quantity, unit_price, comments) VALUES
    (1, 'Onyx Round Coaster',  'ONX-RND-BLK', 50,  3.50, NULL),
    (1, 'Onyx Square Coaster', 'ONX-SQR-GRN', 30,  3.75, NULL),
    (2, 'Marble Ornament',     'MRB-ORN-WHT', 20,  5.00, NULL),
    (2, 'Chess Storage Box',   'CHE-BOX-BRN', 10, 12.00, NULL),
    (2, 'Chess Storage Box',   'CHE-BOX-BLK', 10, 12.00, NULL);

-- Payments
INSERT INTO payments (shipment_header_id, payment_date, description, amount, fee, comments) VALUES
    (1, '2024-01-18', 'AliExpress payment',  245.00, 3.50, 'Paid via PayPal'),
    (2, '2024-02-08', 'AliExpress payment',  460.00, 6.50, 'Paid via PayPal');
