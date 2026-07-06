-- =============================================================
-- Migration: Add vendor invoices per shipment
-- A shipment can receive multiple invoices from different vendors.
-- Payments may optionally be linked to a specific invoice.
--   psql -U postgres -d sales_manager -f 05_add_invoices.sql
-- =============================================================

CREATE TABLE IF NOT EXISTS invoices (
    id                  SERIAL          PRIMARY KEY,
    shipment_header_id  INTEGER         NOT NULL
                            REFERENCES shipment_header(id) ON DELETE CASCADE,
    vendor_name         VARCHAR(255)    NOT NULL,
    invoice_no          VARCHAR(100),
    invoice_date        DATE,
    amount              NUMERIC(18, 2)  NOT NULL,
    comments            TEXT
);

ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS invoice_id INTEGER
        REFERENCES invoices(id) ON DELETE SET NULL;
