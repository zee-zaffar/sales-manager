-- Table: ShipmentHeader
CREATE TABLE ShipmentHeader (
    ID SERIAL PRIMARY KEY,
    SupplierName VARCHAR(255) NOT NULL,
    ShipmentNo VARCHAR(100) NOT NULL,
    DateReceived DATE NOT NULL,
    Comments TEXT
);

-- Table: ShipmentDetail
CREATE TABLE ShipmentDetail (
    ID SERIAL PRIMARY KEY,
    ShipmentHeaderID INTEGER NOT NULL REFERENCES ShipmentHeader(ID) ON DELETE CASCADE,
    Description TEXT,
    SKU VARCHAR(100),
    Quantity INTEGER,
    UnitPrice DECIMAL(18, 2),
    Comments TEXT
);
