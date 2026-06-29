from flask import jsonify
from db_models import ShipmentHeader, ShipmentDetail, Payment
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
    """
    Accepts either a single detail dict or a list of detail dicts.
    Returns a list of inserted detail IDs.
    """
    add_shipment_details = ShipmentDetail(
        shipment_header_id=shipment_header_id,
        description=detail.get('description'),
        sku=detail.get('sku'),
        quantity=detail.get('quantity'),
        unit_price=detail.get('unit_price'),
        comments=detail.get('comments')
    )

    db.session.add(add_shipment_details)      
    db.session.commit()

    return jsonify(shipment_header_id)

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
                "comments": shipment_detail.comments
            }
        }, 200

    except Exception as e:
    # Rollback in case of error
        return {
            "error": "Internal server error",
            "message": f"Failed to update shipment detail: {str(e)}"
        }, 500

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

    return jsonify(payment.id)

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
