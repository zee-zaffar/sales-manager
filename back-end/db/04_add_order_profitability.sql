-- =============================================================
-- Migration: Add profitability fields to orders
-- Run once against the 'sales_manager' database:
--   psql -U postgres -d sales_manager -f 04_add_order_profitability.sql
-- =============================================================

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS cost_of_goods  NUMERIC(18, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS shipping_cost  NUMERIC(18, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS platform_fee   NUMERIC(18, 2) DEFAULT 0;
