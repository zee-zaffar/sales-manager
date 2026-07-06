-- =============================================================
-- Migration: Landed cost model
-- Product cost varies by shipment (goods price + prorated shipping/
-- customs), so it no longer belongs on the products catalog. Invoices
-- are now typed so shipping/customs/other invoices can be prorated
-- across a shipment's line items to compute landed cost per unit;
-- 'product' invoices are already reflected in shipment_detail.unit_price
-- and are excluded from that proration.
--   psql -U postgres -d sales_manager -f 07_landed_cost.sql
-- =============================================================

ALTER TABLE invoices
    ADD COLUMN IF NOT EXISTS invoice_type VARCHAR(20) NOT NULL DEFAULT 'product';

ALTER TABLE products
    DROP COLUMN IF EXISTS cost;
