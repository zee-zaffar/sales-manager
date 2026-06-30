-- =============================================================
-- Sales Manager – Drop Tables
-- WARNING: This will permanently delete all data.
--   psql -U postgres -d sales_manager -f 03_drop_tables.sql
-- =============================================================

DROP TABLE IF EXISTS payments          CASCADE;
DROP TABLE IF EXISTS vendor_invoices   CASCADE;
DROP TABLE IF EXISTS shipment_products CASCADE;
DROP TABLE IF EXISTS shipment_header   CASCADE;
DROP TABLE IF EXISTS orders            CASCADE;
DROP TABLE IF EXISTS products          CASCADE;
DROP TABLE IF EXISTS suppliers         CASCADE;
