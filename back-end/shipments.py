import csv
import io
from flask import jsonify
from db_models import ShipmentHeader, ShipmentDetail, Payment, Invoice, Products
from main import db
from datetime import datetime

def get_all_shipments_header():
    shipment_header = ShipmentHeader.query.all()
    return jsonify([
        {
            'id': p.id,
            'shipment_no': p.shipment_no,
            'supplier_name': p.supplier_name,
            'date_received': p.date_received.isoformat(),
            'comments': p.comments
        } for p in shipment_header
    ])

def get_shipment_by_header_id(shipment_header_id):
    s = ShipmentHeader.query.get_or_404(shipment_header_id)
    return jsonify({
        'id': s.id,
        'supplier_name': s.supplier_name,
        'shipment_no': s.shipment_no,
        'date_received': s.date_received.isoformat(),
        'comments': s.comments
    })

def edit_shipment_header(shipment_header_id: int, data):
    header = ShipmentHeader.query.get(shipment_header_id)
    if not header:
        return {
            "error": "Shipment not found",
            "message": f"No shipment found with ID {shipment_header_id}"
        }, 404

    try:
        header.supplier_name = data.get('supplier_name')
        header.shipment_no = data.get('shipment_no')
        header.date_received = data.get('date_received')
        header.comments = data.get('comments')

        db.session.commit()

        return {
            "success": True,
            "message": "Shipment updated successfully",
            "data": {
                "id": header.id,
                "supplier_name": header.supplier_name,
                "shipment_no": header.shipment_no,
                "date_received": header.date_received.isoformat() if header.date_received else None,
                "comments": header.comments
            }
        }, 200

    except Exception as e:
        return {
            "error": "Internal server error",
            "message": f"Failed to update shipment: {str(e)}"
        }, 500

#Get shipment details by header id
def get_shipment_details(shipment_header_id):
    details = ShipmentDetail.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(ShipmentDetail.description.asc()).all()

    return jsonify([
        {
            'id': d.id,
            'shipment_header_id': d.shipment_header_id,
            'description': d.description,
            'sku': d.sku,
            'quantity': d.quantity,
            'unit_price': float(d.unit_price),
            'landed_cost': float(d.landed_cost) if d.landed_cost is not None else None,
            'comments': d.comments
        } for d in details
    ])

def add_shipment_header(data:any)->int:
    shipment = ShipmentHeader(
        supplier_name=data.get('supplier_name'),
        shipment_no=data.get('shipment_no'),
        date_received=data.get('date_received'),
        comments=data.get('comments')
    )
    db.session.add(shipment)
    db.session.commit()
    return shipment.id

def add_new_shipment_detail(shipment_header_id, detail):
    new_detail = ShipmentDetail(
        shipment_header_id=shipment_header_id,
        description=detail.get('description'),
        sku=detail.get('sku'),
        quantity=detail.get('quantity'),
        unit_price=detail.get('unit_price'),
        landed_cost=detail.get('landed_cost') or None,
        comments=detail.get('comments')
    )

    db.session.add(new_detail)
    db.session.commit()

    return new_detail.id

BULK_UPLOAD_COLUMNS = ['sku', 'description', 'qty', 'unit_price', 'landed_cost', 'comments']

def bulk_add_shipment_details(shipment_header_id, file_stream):
    """
    Parse a CSV of shipment detail rows (columns: sku, description, qty,
    unit_price, landed_cost, comments — header names case-insensitive, spaces
    treated as underscores) and insert them all against the given shipment.
    Any sku not found in the products catalog is left blank rather than
    rejecting the row, so the row still gets recorded and can be assigned a
    product later via Edit. landed_cost is taken as entered, not calculated.
    """
    text = file_stream.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [(h or '').strip().lower().replace(' ', '_') for h in (reader.fieldnames or [])]

    known_codes = {p.code for p in Products.query.all()}

    inserted = 0
    unmatched_skus = []
    errors = []

    for row_num, row in enumerate(reader, start=2):
        sku = (row.get('sku') or '').strip()
        description = (row.get('description') or '').strip()
        qty_raw = (row.get('qty') or row.get('quantity') or '').strip()
        price_raw = (row.get('unit_price') or '').strip()
        landed_cost_raw = (row.get('landed_cost') or '').strip()
        comments = (row.get('comments') or '').strip()

        try:
            quantity = int(qty_raw)
            unit_price = float(price_raw)
            landed_cost = float(landed_cost_raw) if landed_cost_raw else None
        except ValueError:
            errors.append(f"Row {row_num}: invalid qty, unit_price, or landed_cost")
            continue

        if sku and sku not in known_codes:
            unmatched_skus.append({'row': row_num, 'sku': sku, 'description': description})
            sku = ''

        db.session.add(ShipmentDetail(
            shipment_header_id=shipment_header_id,
            description=description or None,
            sku=sku or None,
            quantity=quantity,
            unit_price=unit_price,
            landed_cost=landed_cost,
            comments=comments or None
        ))
        inserted += 1

    db.session.commit()

    return {
        'inserted': inserted,
        'unmatched_skus': unmatched_skus,
        'errors': errors
    }

def edit_shipment_detail(detail_id: int, data):
    """
    Update a shipment detail by ID.
    
    Args:
        detail_id (int): The ID of the shipment detail to update
        
    Returns:
        JSON: Updated shipment detail data or error message
    """

    try:
        # Fetch the existing shipment detail
        shipment_detail = ShipmentDetail.query.get(detail_id)
        if not shipment_detail:
            return {
                "error": "Shipment detail not found",
                "message": f"No shipment detail found with ID {detail_id}"
            }, 40

        shipment_detail.description = data.get('description')
        shipment_detail.sku = data.get('sku')
        shipment_detail.quantity = data.get('quantity')
        shipment_detail.unit_price = data.get('unit_price')
        shipment_detail.landed_cost = data.get('landed_cost') or None
        shipment_detail.comments = data.get('comments')

        db.session.commit()

     # Return the updated shipment detail
        return {
            "success": True,
            "message": "Shipment detail updated successfully",
            "data": {
                "id": shipment_detail.id,
                "shipment_header_id": shipment_detail.shipment_header_id,
                "description": shipment_detail.description,
                "sku": shipment_detail.sku,
                "quantity": shipment_detail.quantity,
                "unit_price": float(shipment_detail.unit_price) if shipment_detail.unit_price else None,
                "landed_cost": float(shipment_detail.landed_cost) if shipment_detail.landed_cost is not None else None,
                "comments": shipment_detail.comments
            }
        }, 200

    except Exception as e:
    # Rollback in case of error
        return {
            "error": "Internal server error",
            "message": f"Failed to update shipment detail: {str(e)}"
        }, 500

def get_invoices_by_shipment_header_id(shipment_header_id):
    invoices = Invoice.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(Invoice.invoice_date.asc()).all()

    return jsonify([
        {
            'id': i.id,
            'shipment_header_id': i.shipment_header_id,
            'vendor_name': i.vendor_name,
            'invoice_no': i.invoice_no,
            'invoice_date': i.invoice_date.isoformat() if i.invoice_date else None,
            'amount': float(i.amount) if i.amount is not None else None,
            'invoice_type': i.invoice_type,
            'comments': i.comments
        } for i in invoices
    ])

def add_new_invoice(shipment_header_id, data) -> int:
    invoice = Invoice(
        shipment_header_id=shipment_header_id,
        vendor_name=data.get('vendor_name'),
        invoice_no=data.get('invoice_no'),
        invoice_date=data.get('invoice_date'),
        amount=data.get('amount'),
        invoice_type=data.get('invoice_type', 'product'),
        comments=data.get('comments')
    )

    db.session.add(invoice)
    db.session.commit()

    return invoice.id

def edit_invoice(invoice_id: int, data):
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {
            "error": "Invoice not found",
            "message": f"No invoice found with ID {invoice_id}"
        }, 404

    try:
        invoice.vendor_name = data.get('vendor_name')
        invoice.invoice_no = data.get('invoice_no')
        invoice.invoice_date = data.get('invoice_date')
        invoice.amount = data.get('amount')
        invoice.invoice_type = data.get('invoice_type', invoice.invoice_type)
        invoice.comments = data.get('comments')

        db.session.commit()

        return {
            "success": True,
            "message": "Invoice updated successfully",
            "data": {
                "id": invoice.id,
                "shipment_header_id": invoice.shipment_header_id,
                "vendor_name": invoice.vendor_name,
                "invoice_no": invoice.invoice_no,
                "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "amount": float(invoice.amount) if invoice.amount is not None else None,
                "invoice_type": invoice.invoice_type,
                "comments": invoice.comments
            }
        }, 200

    except Exception as e:
        return {
            "error": "Internal server error",
            "message": f"Failed to update invoice: {str(e)}"
        }, 500

def delete_invoice(invoice_id: int):
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {
            "error": "Invoice not found",
            "message": f"No invoice found with ID {invoice_id}"
        }, 404

    db.session.delete(invoice)
    db.session.commit()

    return {"success": True, "message": "Invoice deleted successfully"}, 200

def get_all_payments():
    payments = Payment.query.all()
    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
            'invoice_id': p.invoice_id,
            'payment_date': p.payment_date.isoformat(),
            'description': p.description,
            'amount': float(p.amount),
            'fee': float(p.fee),
        }
        for p in payments
    ])

def get_payments_by_shipment_header_id(shipment_header_id):
    payments = Payment.query.filter_by(shipment_header_id=shipment_header_id
                ).order_by(Payment.payment_date.asc()).all()

    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
            'invoice_id': p.invoice_id,
            'invoice_no': p.invoice.invoice_no if p.invoice else None,
            'vendor_name': p.invoice.vendor_name if p.invoice else None,
            'payment_date': p.payment_date.isoformat() if p.payment_date else None,
            'description': p.description,
            'amount': float(p.amount) if p.amount is not None else None,
            'fee': float(p.fee) if p.fee is not None else None,
            'comments': p.comments
        } for p in payments
    ])


def add_new_payment(shipment_header_id,data)->int:
    payment = Payment(
        shipment_header_id=shipment_header_id,
        invoice_id=data.get('invoice_id') or None,
        payment_date=data['payment_date'],
        description=data['description'],
        amount=data['amount'],
        fee=data['fee'],
        comments=data.get('comments')
    )

    db.session.add(payment)
    db.session.commit()

    return payment.id

def edit_payment(payment_id: int, data):
    """
    Update an existing payment record.
    
    Args:
        payment_id (int): The ID of the payment to update
        data (dict): Dictionary containing the updated payment data
        
    Returns:
        tuple: (result_dict, status_code)
        
    Raises:
        ValueError: If input validation fails
        Exception: For database operation errors
    """
    try:
        #Get existing payment record
        payment = Payment.query.get(payment_id)

        payment.invoice_id = data.get('invoice_id') or None
        payment.payment_date = datetime.strptime(data.get('payment_date'), '%Y-%m-%d').date()
        payment.description = data.get('description')
        payment.amount = data.get('amount')
        payment.fee = data.get('fee')
        payment.comments = data.get('comments')

        db.session.commit()

        return {
            "success": True,
            "message": "Payment updated successfully",
            "data": {
                "id": payment.id,
                "shipment_header_id": payment.shipment_header_id,
                "invoice_id": payment.invoice_id,
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "description": payment.description,
                "amount": float(payment.amount) if payment.amount is not None else None,
                "fee": float(payment.fee) if payment.fee is not None else None,
                "comments": payment.comments
            }
        }, 200
    
    except Exception as e:
    # Rollback in case of error
        return {
            "error": "Internal server error",
            "message": f"Failed to update payment: {str(e)}"
        }, 500

def delete_payment(payment_id: int):
    payment = Payment.query.get(payment_id)
    if not payment:
        return {
            "error": "Payment not found",
            "message": f"No payment found with ID {payment_id}"
        }, 404

    db.session.delete(payment)
    db.session.commit()

    return {"success": True, "message": "Payment deleted successfully"}, 200
