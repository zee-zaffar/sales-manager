-- =============================================================
-- Migration: Data-integrity constraints for shipments / invoices / payments
-- Backstop for the validation done in shipments.py. Safe to re-run.
--   psql -U postgres -d sales_manager -f 11_shipment_integrity.sql
--
-- Not enforced here (enforced in application code for new/edited rows,
-- because older data may violate them):
--   * payment.invoice_id must belong to the same shipment as the payment
--   * sum(payments) <= invoice amount
-- =============================================================

-- One shipment number per supplier
ALTER TABLE shipment_header
    DROP CONSTRAINT IF EXISTS uq_shipment_supplier_no,
    ADD CONSTRAINT uq_shipment_supplier_no UNIQUE (supplier_name, shipment_no);

-- Line items: positive quantity, non-negative prices
ALTER TABLE shipment_detail
    DROP CONSTRAINT IF EXISTS ck_detail_quantity_positive,
    DROP CONSTRAINT IF EXISTS ck_detail_unit_price_nonneg,
    DROP CONSTRAINT IF EXISTS ck_detail_landed_cost_nonneg,
    ADD CONSTRAINT ck_detail_quantity_positive CHECK (quantity > 0),
    ADD CONSTRAINT ck_detail_unit_price_nonneg CHECK (unit_price >= 0),
    ADD CONSTRAINT ck_detail_landed_cost_nonneg CHECK (landed_cost IS NULL OR landed_cost >= 0);

-- Invoices: valid type, positive amount
ALTER TABLE invoices
    DROP CONSTRAINT IF EXISTS ck_invoice_type,
    DROP CONSTRAINT IF EXISTS ck_invoice_amount_positive,
    ADD CONSTRAINT ck_invoice_type CHECK (invoice_type IN ('product', 'shipping', 'customs', 'other')),
    ADD CONSTRAINT ck_invoice_amount_positive CHECK (amount > 0);

-- No duplicate invoice number per vendor per shipment
CREATE UNIQUE INDEX IF NOT EXISTS uq_invoice_vendor_no
    ON invoices (shipment_header_id, vendor_name, invoice_no)
    WHERE invoice_no IS NOT NULL;

-- Payments: positive amount, non-negative fee
ALTER TABLE payments
    DROP CONSTRAINT IF EXISTS ck_payment_amount_positive,
    DROP CONSTRAINT IF EXISTS ck_payment_fee_nonneg,
    ADD CONSTRAINT ck_payment_amount_positive CHECK (amount > 0),
    ADD CONSTRAINT ck_payment_fee_nonneg CHECK (fee >= 0);

-- An invoice that has payments can no longer be deleted (previously the
-- payment was silently detached via ON DELETE SET NULL). Deleting a whole
-- shipment still cascades to its invoices and payments.
ALTER TABLE payments
    DROP CONSTRAINT IF EXISTS payments_invoice_id_fkey,
    ADD CONSTRAINT payments_invoice_id_fkey
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE NO ACTION;
