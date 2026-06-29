-- =============================================================
-- Sales Manager – Create Tables
-- Run against the 'sales_manager' database:
--   psql -U postgres -d sales_manager -f 01_create_tables.sql
-- =============================================================

-- Products catalogue
CREATE TABLE IF NOT EXISTS products (
    code        VARCHAR(100)    PRIMARY KEY,
    category    VARCHAR(255)    NOT NULL,
    description VARCHAR(255)    NOT NULL,
    color       VARCHAR(100)    NOT NULL,
    cost        NUMERIC(18, 2)  NOT NULL,
    comments    TEXT
);

-- Sales orders (sourced from Etsy receipts or manual entry)
CREATE TABLE IF NOT EXISTS orders (
    order_no        VARCHAR(100)    PRIMARY KEY,
    order_date      DATE            NOT NULL,
    qty             INTEGER         NOT NULL,
    color           VARCHAR(100),
    source          VARCHAR(100),
    platform        VARCHAR(100),
    order_amount    NUMERIC(18, 2),
    sales_tax       NUMERIC(18, 2),
    comments        TEXT
);

-- Shipment header (one record per supplier delivery)
CREATE TABLE IF NOT EXISTS shipment_header (
    id              SERIAL          PRIMARY KEY,
    supplier_name   VARCHAR(255)    NOT NULL,
    shipment_no     VARCHAR(100)    NOT NULL,
    date_received   DATE            NOT NULL,
    comments        TEXT
);

-- Shipment line items
CREATE TABLE IF NOT EXISTS shipment_detail (
    id                  SERIAL          PRIMARY KEY,
    shipment_header_id  INTEGER         NOT NULL
                            REFERENCES shipment_header(id) ON DELETE CASCADE,
    description         TEXT,
    sku                 VARCHAR(100),
    quantity            INTEGER,
    unit_price          NUMERIC(18, 2),
    comments            TEXT
);

-- Payments against a shipment
CREATE TABLE IF NOT EXISTS payments (
    id                  SERIAL          PRIMARY KEY,
    shipment_header_id  INTEGER         NOT NULL
                            REFERENCES shipment_header(id) ON DELETE CASCADE,
    payment_date        DATE            NOT NULL,
    description         VARCHAR(100)    NOT NULL,
    amount              NUMERIC(18, 2)  NOT NULL,
    fee                 NUMERIC(18, 2)  NOT NULL,
    comments            TEXT
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id              SERIAL          PRIMARY KEY,
    name            VARCHAR(255)    NOT NULL,
    contact_name    VARCHAR(255),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    address         TEXT,
    comments        TEXT
);
