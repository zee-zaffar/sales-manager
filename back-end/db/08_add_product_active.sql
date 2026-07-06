-- =============================================================
-- Migration: Active/inactive flag for products
-- Only active products should be selectable when adding a new
-- shipment detail line, so discontinued products stop showing up
-- without deleting their history.
--   psql -U postgres -d sales_manager -f 08_add_product_active.sql
-- =============================================================

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT true;
