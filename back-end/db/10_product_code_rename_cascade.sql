-- =============================================================
-- Migration: Allow renaming a product's code
-- orders.sku references products.code; without ON UPDATE CASCADE,
-- renaming a product's code would fail if any order references it.
-- shipment_detail.sku has no FK (by design, to tolerate SKUs that
-- predate the catalog), so it's updated manually in application code
-- when a product is renamed.
--   psql -U postgres -d sales_manager -f 10_product_code_rename_cascade.sql
-- =============================================================

ALTER TABLE orders
    DROP CONSTRAINT orders_sku_fkey,
    ADD CONSTRAINT orders_sku_fkey
        FOREIGN KEY (sku) REFERENCES products(code)
        ON DELETE SET NULL ON UPDATE CASCADE;
