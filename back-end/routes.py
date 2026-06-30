from main import app
from flask import request, jsonify, send_file
from products import get_all_products, add_new_product
from shipments import (
    get_all_shipments_header, get_all_payments, get_payments_by_shipment_header_id,
    get_shipment_by_header_id, add_shipment_header, add_shipment_product,
    get_shipment_products, add_new_payment, edit_shipment_product, edit_payment,
    delete_shipment_header, edit_shipment_header,
    delete_shipment_product, delete_payment,
    get_invoices_by_shipment, add_invoice, edit_invoice, delete_invoice,
    get_products_csv_template, bulk_add_products
)
from orders import get_orders, insert_order, get_order_by_no, update_order
from etsy import get_receipt
from api_models import Receipt
from suppliers import get_all_suppliers, add_new_supplier, update_supplier

# Route to get all orders
@app.route('/orders', methods=['GET'])
def orders_list():
    return get_orders()

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

    for product in payload.get('Details'):
        add_shipment_product(shipment_header_id, product)
  
    return jsonify({'id': shipment_header_id}), 201

@app.route('/shipments/<int:shipment_header_id>', methods=['GET'])
def get_shipment(shipment_header_id):
    return get_shipment_by_header_id(shipment_header_id)

@app.route('/shipments/<int:shipment_header_id>', methods=['PUT'])
def update_shipment(shipment_header_id):
    data = request.json
    result, status_code = edit_shipment_header(shipment_header_id, data)
    return jsonify(result), status_code

@app.route('/shipments/<int:shipment_header_id>', methods=['DELETE'])
def delete_shipment(shipment_header_id):
    result, status_code = delete_shipment_header(shipment_header_id)
    return jsonify(result), status_code

# Get shipment products
@app.route('/shipments/<int:shipment_header_id>/products', methods=['GET'])
def shipment_products(shipment_header_id: int):
    return get_shipment_products(shipment_header_id)

# Add shipment product
@app.route('/shipments/<int:shipment_header_id>/products', methods=['POST'])
def add_shipment_product_route(shipment_header_id: int):
    product_id = add_shipment_product(shipment_header_id, request.json)
    return jsonify({'id': product_id}), 201

# Delete shipment product
@app.route('/shipments/<int:header_id>/products/<int:product_id>', methods=['DELETE'])
def remove_shipment_product(header_id: int, product_id: int):  # noqa: ARG001
    result, status_code = delete_shipment_product(product_id)
    return jsonify(result), status_code

# Update shipment product
@app.route('/shipments/<int:header_id>/products/<int:product_id>', methods=['PUT'])
def update_shipment_product(header_id: int, product_id: int):  # noqa: ARG001
    result, status_code = edit_shipment_product(product_id, request.json)
    return jsonify(result), status_code

# Add new payment
@app.route('/shipments/<int:shipment_header_id>/payments', methods=['POST'])
def add_payment(shipment_header_id: int):
    payment = request.json
    payment_id = add_new_payment(shipment_header_id, payment)
    return jsonify({'id': payment_id}), 201

@app.route('/shipments/<int:header_id>/payments/<int:payment_id>', methods=['DELETE'])
def remove_payment(header_id: int, payment_id: int):  # noqa: ARG001
    result, status_code = delete_payment(payment_id)
    return jsonify(result), status_code

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

#Get all payments
@app.route('/payments', methods=['GET'])
def get_payments():
    return get_all_payments()

#Get all products
@app.route('/products', methods=['GET'])
def get_products():
    return get_all_products()

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

# CSV template download for shipment products
@app.route('/shipments/products/template', methods=['GET'])
def products_csv_template():
    return get_products_csv_template()

# Bulk upload products from CSV
@app.route('/shipments/<int:shipment_header_id>/products/upload', methods=['POST'])
def upload_products_csv(shipment_header_id: int):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'File must be a .csv'}), 400
    result = bulk_add_products(shipment_header_id, file.read())
    return jsonify(result), 200

# Invoice routes
@app.route('/shipments/<int:shipment_header_id>/invoices', methods=['GET'])
def get_invoices(shipment_header_id: int):
    return get_invoices_by_shipment(shipment_header_id)

@app.route('/shipments/<int:shipment_header_id>/invoices', methods=['POST'])
def add_invoice_route(shipment_header_id: int):
    data = request.json
    invoice_id = add_invoice(shipment_header_id, data)
    return jsonify({'id': invoice_id}), 201

@app.route('/shipments/<int:header_id>/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(header_id: int, invoice_id: int):  # noqa: ARG001
    result, status_code = edit_invoice(invoice_id, request.json)
    return jsonify(result), status_code

@app.route('/shipments/<int:header_id>/invoices/<int:invoice_id>', methods=['DELETE'])
def remove_invoice(header_id: int, invoice_id: int):  # noqa: ARG001
    result, status_code = delete_invoice(invoice_id)
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
