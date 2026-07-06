-- =============================================================
-- Migration: Manual landed cost per shipment detail line
-- Landed cost is entered directly (from the user's own numbers),
-- not auto-calculated by prorating shipping/customs invoices.
--   psql -U postgres -d sales_manager -f 09_manual_landed_cost.sql
-- =============================================================

ALTER TABLE shipment_detail
    ADD COLUMN IF NOT EXISTS landed_cost NUMERIC(18, 2);
