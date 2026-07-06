from main import app
from flask import request, jsonify
from products import get_all_products, add_new_product, update_product_active, update_product, delete_product
from shipments import get_all_shipments_header, get_all_payments, get_payments_by_shipment_header_id, get_shipment_by_header_id, add_shipment_header, add_new_shipment_detail, bulk_add_shipment_details, get_shipment_details, add_new_payment, edit_shipment_detail, edit_payment, get_invoices_by_shipment_header_id, add_new_invoice, edit_invoice, delete_invoice, delete_payment, edit_shipment_header
from orders import get_orders, insert_order, get_order_by_no, update_order, get_monthly_summary
from etsy import get_receipt
from api_models import Receipt
from suppliers import get_all_suppliers, add_new_supplier, update_supplier
from inventory import get_inventory

# Route to get all orders
@app.route('/orders', methods=['GET'])
def orders_list():
    return get_orders()

# Monthly profit summary
@app.route('/orders/monthly-summary', methods=['GET'])
def orders_monthly_summary():
    return get_monthly_summary()

# Route to get all orders
@app.route('/etsy/receipts/<int:receipt_id>', methods=['GET'])
def get_etsy_receipt(receipt_id):
    etsy_receipt =  get_receipt(receipt_id)
    return jsonify(etsy_receipt), 200

# Route to get an order by order_no
@app.route('/orders/<order_no>', methods=['GET'])
def order_get(order_no):
    return get_order_by_no(order_no)

# Route to update an order via PUT
@app.route('/orders/<order_no>', methods=['PUT'])
def order_update(order_no):
    return update_order(order_no)

# Route to insert a new order
@app.route('/orders', methods=['POST'])
def orders_insert():
    return insert_order()

@app.route('/shipments', methods=['GET'])
def get_shipments():
    return get_all_shipments_header()

#Add new shipment
@app.route('/shipments', methods=['POST'])
def add_new_shipment():
    payload = request.json
    shipment_header_id = shipment_header_id =  add_shipment_header(payload)
    print ("New Shipment Header ID:", shipment_header_id)

    # Loop through details and add each one
    for shipment_detail in payload.get('Details'):
        add_new_shipment_detail(shipment_header_id, shipment_detail)
  
    return jsonify({'id': shipment_header_id}), 201

@app.route('/shipments/<int:shipment_header_id>', methods=['GET'])
def get_shipment(shipment_header_id):
   return get_shipment_by_header_id(shipment_header_id)

# Update shipment header
@app.route('/shipments/<int:shipment_header_id>', methods=['PUT'])
def update_shipment_header_route(shipment_header_id: int):
    update_data = request.json
    result, status_code = edit_shipment_header(shipment_header_id, update_data)
    return jsonify(result), status_code

#Get shipment details by header id
@app.route('/shipments/<int:shipment_header_id>/details', methods=['GET'])
def shipment_details(shipment_header_id:int):
    return get_shipment_details(shipment_header_id)

# Add new shipment detail
@app.route('/shipments/<int:shipment_header_id>/details', methods=['POST'])
def add_shipment_detail(shipment_header_id: int):
    shipment_detail = request.json
    detail_id = add_new_shipment_detail(shipment_header_id, shipment_detail)
    return jsonify({'id': detail_id}), 201

# Bulk-upload shipment details from a CSV
@app.route('/shipments/<int:shipment_header_id>/details/bulk-upload', methods=['POST'])
def bulk_upload_shipment_details(shipment_header_id: int):
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    result = bulk_add_shipment_details(shipment_header_id, request.files['file'].stream)
    return jsonify(result), 201

# Update shipment detail
@app.route('/shipments/<int:header_id>/details/<int:detail_id>', methods=['PUT'])
def update_shipment_detail(header_id: int, detail_id: int):

    # Get the update data from request
    update_data = request.json

    result, status_code = edit_shipment_detail(detail_id, update_data)

    return jsonify(result), status_code

# Add new payment
@app.route('/shipments/<int:shipment_header_id>/payments', methods=['POST'])
def add_payment(shipment_header_id: int):
    payment = request.json
    payment_id = add_new_payment(shipment_header_id, payment)
    return jsonify({'id': payment_id}), 201

# Update payment
@app.route('/shipments/<int:header_id>/payments/<int:payment_id>', methods=['PUT'])
def update_payment_route(header_id: int, payment_id: int):
    """
    Update a payment for a specific shipment.
    
    Args:
        shipment_id (int): The ID of the shipment header
        payment_id (int): The ID of the payment to update
        
    Returns:
        JSON: Updated payment data or error message with appropriate HTTP status code
    """
    # Get the update data from request
    update_data = request.json
    
    # Call the update function
    result, status_code = edit_payment(payment_id, update_data)

    return jsonify(result), status_code

# Delete payment
@app.route('/shipments/<int:header_id>/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment_route(header_id: int, payment_id: int):
    result, status_code = delete_payment(payment_id)
    return jsonify(result), status_code

#Get invoices for a shipment
@app.route('/shipments/<int:shipment_header_id>/invoices', methods=['GET'])
def get_invoices_for_shipment(shipment_header_id: int):
    return get_invoices_by_shipment_header_id(shipment_header_id)

# Add new invoice
@app.route('/shipments/<int:shipment_header_id>/invoices', methods=['POST'])
def add_invoice(shipment_header_id: int):
    invoice = request.json
    invoice_id = add_new_invoice(shipment_header_id, invoice)
    return jsonify({'id': invoice_id}), 201

# Update invoice
@app.route('/shipments/<int:header_id>/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice_route(header_id: int, invoice_id: int):
    update_data = request.json
    result, status_code = edit_invoice(invoice_id, update_data)
    return jsonify(result), status_code

# Delete invoice
@app.route('/shipments/<int:header_id>/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice_route(header_id: int, invoice_id: int):
    result, status_code = delete_invoice(invoice_id)
    return jsonify(result), status_code

#Get all payments
@app.route('/payments', methods=['GET'])
def get_payments():
    return get_all_payments()

#Get all products
@app.route('/products', methods=['GET'])
def get_products():
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    return get_all_products(active_only=active_only)

# Toggle a product's active status
@app.route('/products/<code>/active', methods=['PUT'])
def update_product_active_route(code):
    data = request.json
    result, status_code = update_product_active(code, data.get('active'))
    return jsonify(result), status_code

# Get computed inventory (received via shipments minus ordered)
@app.route('/inventory', methods=['GET'])
def inventory_list():
    return get_inventory()

@app.route('/shipments/<int:shipment_header_id>/payments', methods=['GET'])
def get_payments_for_shipment(shipment_header_id: int):
    return get_payments_by_shipment_header_id(shipment_header_id)

# Route to add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    print("Received data for new product:", data)
    product_code =  add_new_product(data)
    return jsonify({'product_code': product_code}), 201

# Update a product
@app.route('/products/<code>', methods=['PUT'])
def update_product_route(code):
    data = request.json
    result, status_code = update_product(code, data)
    return jsonify(result), status_code

# Delete a product
@app.route('/products/<code>', methods=['DELETE'])
def delete_product_route(code):
    result, status_code = delete_product(code)
    return jsonify(result), status_code

# Supplier routes
@app.route('/suppliers', methods=['GET'])
def suppliers_list():
    return get_all_suppliers()

@app.route('/suppliers', methods=['POST'])
def suppliers_add():
    return add_new_supplier()

@app.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def supplier_update(supplier_id):
    return update_supplier(supplier_id)
