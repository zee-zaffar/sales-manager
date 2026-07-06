-- =============================================================
-- Migration: Link orders to a product SKU for inventory deduction
-- Existing orders predate this field and are left NULL; the SKU
-- should be set going forward via the order entry form.
--   psql -U postgres -d sales_manager -f 06_add_order_sku.sql
-- =============================================================

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS sku VARCHAR(100)
        REFERENCES products(code) ON DELETE SET NULL;
