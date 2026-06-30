import csv
import io
from flask import jsonify, send_file
from db_models import ShipmentHeader, ShipmentProduct, Payment, VendorInvoice
from main import db
from datetime import datetime

CSV_COLUMNS = ['Description', 'SKU', 'Quantity', 'Unit Price', 'Comments']

def get_products_csv_template():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)
    writer.writerow(['Example Product Name', 'PROD-001', '10', '25.00', 'Optional notes'])
    output.seek(0)
    bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
    return send_file(bytes_output, mimetype='text/csv', as_attachment=True, download_name='shipment_products_template.csv')

def bulk_add_products(shipment_header_id: int, file_bytes: bytes):
    content = file_bytes.decode('utf-8-sig')  # utf-8-sig strips Excel BOM
    reader = csv.DictReader(io.StringIO(content))
    added = 0
    errors = []
    for i, row in enumerate(reader, start=2):
        desc = row.get('Description', '').strip()
        sku  = row.get('SKU', '').strip()
        if not desc and not sku:
            continue  # skip blank rows
        try:
            product = ShipmentProduct(
                shipment_header_id=shipment_header_id,
                description=desc,
                sku=sku,
                quantity=int(row.get('Quantity', 0) or 0),
                unit_price=float(row.get('Unit Price', 0) or 0),
                comments=row.get('Comments', '').strip() or None
            )
            db.session.add(product)
            added += 1
        except Exception as e:
            errors.append(f"Row {i}: {e}")
    if added:
        db.session.commit()
    return {'added': added, 'errors': errors}

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

#Get shipment details by header id
def get_shipment_products(shipment_header_id):
    products = ShipmentProduct.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(ShipmentProduct.description.asc()).all()

    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
            'description': p.description,
            'sku': p.sku,
            'quantity': p.quantity,
            'unit_price': float(p.unit_price),
            'comments': p.comments
        } for p in products
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

def add_shipment_product(shipment_header_id, product):
    new_product = ShipmentProduct(
        shipment_header_id=shipment_header_id,
        description=product.get('description'),
        sku=product.get('sku'),
        quantity=product.get('quantity'),
        unit_price=product.get('unit_price'),
        comments=product.get('comments')
    )

    db.session.add(new_product)
    db.session.commit()

    return new_product.id

def edit_shipment_product(product_id: int, data):
    try:
        product = ShipmentProduct.query.get(product_id)
        if not product:
            return {"error": f"Product {product_id} not found"}, 404

        product.description = data.get('description')
        product.sku = data.get('sku')
        product.quantity = data.get('quantity')
        product.unit_price = data.get('unit_price')
        product.comments = data.get('comments')

        db.session.commit()

        return {
            "success": True,
            "data": {
                "id": product.id,
                "shipment_header_id": product.shipment_header_id,
                "description": product.description,
                "sku": product.sku,
                "quantity": product.quantity,
                "unit_price": float(product.unit_price) if product.unit_price else None,
                "comments": product.comments
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update product: {str(e)}"}, 500

def get_all_payments():
    payments = Payment.query.all()
    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
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
        payment_date=data['payment_date'],
        description=data['description'],
        amount=data['amount'],
        fee=data['fee'],
        comments=data.get('comments')
    )

    db.session.add(payment)
    db.session.commit()

    return payment.id

def delete_shipment_header(shipment_header_id: int):
    shipment = ShipmentHeader.query.get(shipment_header_id)
    if not shipment:
        return {"error": "Shipment not found"}, 404
    db.session.delete(shipment)
    db.session.commit()
    return {"success": True}, 200

def edit_shipment_header(shipment_header_id: int, data):
    shipment = ShipmentHeader.query.get(shipment_header_id)
    if not shipment:
        return {"error": "Shipment not found"}, 404
    shipment.supplier_name = data.get('supplier_name', shipment.supplier_name)
    shipment.shipment_no = data.get('shipment_no', shipment.shipment_no)
    shipment.date_received = data.get('date_received', shipment.date_received)
    shipment.comments = data.get('comments', shipment.comments)
    db.session.commit()
    return {
        "success": True,
        "data": {
            "id": shipment.id,
            "supplier_name": shipment.supplier_name,
            "shipment_no": shipment.shipment_no,
            "date_received": shipment.date_received.isoformat(),
            "comments": shipment.comments
        }
    }, 200

def delete_shipment_product(product_id: int):
    product = ShipmentProduct.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404
    db.session.delete(product)
    db.session.commit()
    return {"success": True}, 200

def delete_payment(payment_id: int):
    payment = Payment.query.get(payment_id)
    if not payment:
        return {"error": "Payment not found"}, 404
    db.session.delete(payment)
    db.session.commit()
    return {"success": True}, 200

def get_invoices_by_shipment(shipment_header_id: int):
    invoices = VendorInvoice.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(VendorInvoice.invoice_date.asc()).all()
    return jsonify([
        {
            'id': i.id,
            'shipment_header_id': i.shipment_header_id,
            'invoice_no': i.invoice_no,
            'invoice_date': i.invoice_date.isoformat(),
            'description': i.description,
            'amount': float(i.amount),
            'comments': i.comments
        } for i in invoices
    ])

def add_invoice(shipment_header_id: int, data) -> int:
    invoice = VendorInvoice(
        shipment_header_id=shipment_header_id,
        invoice_no=data['invoice_no'],
        invoice_date=data['invoice_date'],
        description=data.get('description'),
        amount=data['amount'],
        comments=data.get('comments')
    )
    db.session.add(invoice)
    db.session.commit()
    return invoice.id

def edit_invoice(invoice_id: int, data):
    invoice = VendorInvoice.query.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404
    invoice.invoice_no = data.get('invoice_no', invoice.invoice_no)
    invoice.invoice_date = datetime.strptime(data.get('invoice_date'), '%Y-%m-%d').date()
    invoice.description = data.get('description', invoice.description)
    invoice.amount = data.get('amount', invoice.amount)
    invoice.comments = data.get('comments', invoice.comments)
    db.session.commit()
    return {
        "success": True,
        "data": {
            "id": invoice.id,
            "shipment_header_id": invoice.shipment_header_id,
            "invoice_no": invoice.invoice_no,
            "invoice_date": invoice.invoice_date.isoformat(),
            "description": invoice.description,
            "amount": float(invoice.amount),
            "comments": invoice.comments
        }
    }, 200

def delete_invoice(invoice_id: int):
    invoice = VendorInvoice.query.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404
    db.session.delete(invoice)
    db.session.commit()
    return {"success": True}, 200

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
