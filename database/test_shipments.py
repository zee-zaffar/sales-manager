from shipments import add_shipment_header, add_shipment_detail
from datetime import date

if __name__ == "__main__":
    # Insert a shipment header
    header_id = add_shipment_header(
        supplier_name="Acme Supplies",
        shipment_no="SHIP12345",
        date_received=date.today(),
        comments="First test shipment"
    )
    print(f"Inserted ShipmentHeader with ID: {header_id}")

    # Insert two shipment details for the above header
    detail1_id = add_shipment_detail(
        header_id=header_id,
        description="Widget A",
        sku="WIDGET-A-001",
        quantity=10,
        unit_price=2.50,
        comments="Blue color"
    )
    print(f"Inserted ShipmentDetail with ID: {detail1_id}")

    detail2_id = add_shipment_detail(
        header_id=header_id,
        description="Widget B",
        sku="WIDGET-B-002",
        quantity=5,
        unit_price=5.00,
        comments="Red color"
    )
    print(f"Inserted ShipmentDetail with ID: {detail2_id}")
