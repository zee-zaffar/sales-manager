
import os
from flask import Flask, flash, redirect, render_template, request, url_for
import requests
from dotenv import load_dotenv
# from api.oauth_token import get_refresh_token
from business.orders import process_receipts

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-very-secret-key")  # Change this to a strong, random value in production

sales_manager_api_url = os.getenv("SALES_MANAGER_API_URL", "").rstrip("/")
    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():
    try:
        response = requests.get(f"{sales_manager_api_url}/products")
        response.raise_for_status()
        products = response.json()
        
    except Exception as e:
        print(f"Error fetching products: {e}")
       
    return render_template("products_list.html", products = products)

@app.route("/process_receipts")
def get_receipts():
    # Process Etsy receipts from utils\receipts.txt file
    return process_receipts()

@app.route("/suppliers")
def suppliers():
    return render_template("suppliers.html")

# Get all shipments
@app.route("/shipments")
def shipments():
    shipments = []
    try:
        response = requests.get(f"{sales_manager_api_url}/shipments")
        response.raise_for_status()
        shipments = response.json()
    except Exception as e:
        print(f"Error fetching shipments: {e}")
    return render_template("shipments_list.html", shipments=shipments)

# Get a single shipment header with associated details and payments
@app.route("/shipments/<int:shipment_id>")
def shipment_details(shipment_id):
    shipment = {}
    details = []
    payments = []
    try:
        response = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}")
        response.raise_for_status()
        shipment = response.json()

        response2 = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}/details")
        response2.raise_for_status()
        details = response2.json()

        response3 = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}/payments")
        response3.raise_for_status()
        payments = response3.json()
    except Exception as e:
        print(f"Error fetching shipment details/payments: {e}")

    details_grand_total = sum(d['quantity'] * d['unit_price'] for d in details)
    payments_grand_total = sum(p['amount'] + p['fee'] for p in payments)
    return render_template(
        'shipment_details.html',
        shipment=shipment,
        details=details,
        payments=payments,
        details_grand_total=details_grand_total,
        payments_grand_total=payments_grand_total
    )

# Route to add new shipment form
@app.route('/shipment/new')
def new_shipment():
    return render_template('shipment_entry.html')

# Handle new shipment header and details form submit
@app.route('/shipment/new', methods=['POST'])
def submit_shipment():
    # Get header fields
    supplier_name = request.form.get('supplier_name')
    shipment_no = request.form.get('shipment_no')
    date_received = request.form.get('date_received')
    comments = request.form.get('comments')

    # Get details (multiple rows)
    descriptions = request.form.getlist('description[]')
    skus = request.form.getlist('sku[]')
    quantities = request.form.getlist('quantity[]')
    unit_prices = request.form.getlist('unit_price[]')
    detail_comments = request.form.getlist('detail_comments[]')

    details = []
    for desc, sku, qty, price, comm in zip(descriptions, skus, quantities, unit_prices, detail_comments):
        details.append({
            "Description": desc,
            "SKU": sku,
            "Quantity": int(qty),
            "UnitPrice": float(price),
            "Comments": comm
        })

    # Prepare payload for API
    payload = {
        "SupplierName": supplier_name,
        "ShipmentNo": shipment_no,
        "DateReceived": date_received,
        "Comments": comments,
        "Details": details
    }

    # Send POST request to API
    api_url = f"{sales_manager_api_url}/shipments"
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 201:
            flash('Shipment added successfully!')
        else:
            flash('Failed to add shipment.')
    except Exception as e:
        print(f"Error posting shipment: {e}")
        flash('Failed to add shipment.')
    return redirect(url_for('shipments'))

# Route to add new payment form
@app.route('/shipments/<int:shipment_id>/payment/new')
def new_payment(shipment_id):
    return render_template('payment_entry.html', shipment_id=shipment_id)

# Update shipment detail form submit
@app.route('/shipments/<int:header_id>/details/update', methods=['POST'])
def update_detail_modal(header_id):

    detail_id = request.form.get('detail_id')

    try:
        data = {
            'detail_id': detail_id,
            'description': request.form.get('description'),
            'sku': request.form.get('sku'),
            'quantity': request.form.get('quantity'),
            'unit_price': request.form.get('unit_price'),
            'comments': request.form.get('comments')
        }
        
        response = requests.put(f"{sales_manager_api_url}/shipments/{header_id}/details/{detail_id}", json=data)
        response.raise_for_status()
        
        flash('Shipment detail updated successfully!', 'success')
    except Exception as e:
        print(f"Error updating shipment detail: {e}")
        flash('Error updating shipment detail.', 'error')
    
    return redirect(url_for('shipment_details', shipment_id=header_id))

# update payment form submit
@app.route('/shipments/<int:header_id>/payments/update', methods=['POST'])
def update_payment_modal(header_id):

    payment_id = int(request.form.get('payment_id'))
    try:
        data = {
            'payment_id': request.form.get('payment_id'),
            'payment_date': request.form.get('payment_date'),
            'description': request.form.get('description'),
            'amount': request.form.get('amount'),
            'fee': request.form.get('fee'),
            'comments': request.form.get('comments')
        }
        
        response = requests.put(f"{sales_manager_api_url}/shipments/{header_id}/payments/{payment_id}", json=data)
        response.raise_for_status()
        
        flash('Payment updated successfully!', 'success')
    except Exception as e:
        print(f"Error updating payment: {e}")
        flash('Error updating payment.', 'error')
    
    return redirect(url_for('shipment_details', shipment_id=header_id))

# Add new payment form submit
@app.route('/shipments/<int:shipment_header_id>/payments/add', methods=['POST'])
def add_payment_modal(shipment_header_id):
    new_payment = {
        "payment_date": request.form.get('payment_date'),
        "description": request.form.get('description'),
        "amount": request.form.get('amount'),
        "fee": request.form.get('fee'),
        "comments": request.form.get('comments')
    }

    api_url = f"{sales_manager_api_url}/shipments/{shipment_header_id}/payments"
    try:
        response = requests.post(api_url, json=new_payment)
        if response.status_code == 201:
            flash('Payment added successfully!')
        else:
            flash('Failed to add payment')
    except Exception as e:
        print(f"Error adding payment: {e}")
        flash('Failed to add new payment')

    return redirect(url_for('shipment_details', shipment_id=shipment_header_id))

# Add new shipment detail form submit
@app.route('/shipments/<int:shipment_header_id>/details/add', methods=['POST'])
def add_detail_modal(shipment_header_id):
    shipment_detail = {
        "Description": request.form.get('Description'),
        "SKU": request.form.get('SKU'),
        "Quantity": request.form.get('Quantity'),
        "UnitPrice": request.form.get('UnitPrice'),
        "Comments": request.form.get('Comments')
    }

    api_url = f"{sales_manager_api_url}/shipments/{shipment_header_id}/details"
    try:
        response = requests.post(api_url, json=shipment_detail)
        if response.status_code == 201:
            flash('Shipment details added successfully!')
        else:
            flash('Failed to add shipment details.')
    except Exception as e:
        print(f"Error adding shipment detail: {e}")
        flash('Failed to add shipment details.')

    return redirect(url_for('shipments'))

# Route to handle new product form submission
@app.route('/products/new', methods=['POST'])
def add_product():
    # Map form fields to API fields
    try:
        product = {
            "code": request.form.get('code'),
            "category": request.form.get('category'),
            "cost": float(request.form.get('cost', 0)),
            "description": request.form.get('description'),
            "color": request.form.get('color', ''),
            "comments": request.form.get('comments', '')
        }
    except Exception:
        return {"success": False, "error": "Invalid product fields"}, 400

    api_url = f"{sales_manager_api_url}/products"
    try:
        response = requests.post(api_url, json=product)
        response.raise_for_status()
        return {"success": True}, 201
    except Exception as e:
        print(f"Error adding product: {e}")
        return {"success": False, "error": str(e)}, 400

# Route to get all orders
@app.route('/orders')
def orders():
    orders = []
    try:
        response = requests.get(f"{sales_manager_api_url}/orders")
        response.raise_for_status()
        orders = response.json()
    except Exception as e:
        print(f"Error fetching orders: {e}")
    return render_template("orders.html", orders=orders)

# Route to add a new order
@app.route('/add_order', methods=['POST'])
def add_order():
    try:
        order = {
            "order_no": request.form.get('order_no'),
            "order_date": request.form.get('order_date'),
            "order_amount": float(request.form.get('order_amount', 0)),
            "qty": int(request.form.get('qty', 0)),
            "sales_tax": float(request.form.get('sales_tax', 0)),
            "platform": request.form.get('platform'),
            "source": request.form.get('source'),
            "color": request.form.get('color', ''),
            "comments": request.form.get('comments', '')
        }
    except Exception as e:
        print(f"Invalid order payload: {e}")
        return {"success": False, "error": "Invalid payload"}, 400

    # Call backend API to insert order
    backend_api_url = f"{sales_manager_api_url}/orders"
    try:
        backend_response = requests.post(backend_api_url, json=order)
        backend_response.raise_for_status()
        return {"success": True}, 201
    except Exception as e:
        print(f"Error adding order via backend API: {e}")
        return {"success": False, "error": str(e)}, 400

# Route to update an existing order
@app.route('/update_order', methods=['POST'])
def update_order():
    try:
        order = {
            "order_no": request.form.get('order_no'),
            "order_date": request.form.get('order_date'),
            "order_amount": float(request.form.get('order_amount', 0)),
            "qty": int(request.form.get('qty', 0)),
            "sales_tax": float(request.form.get('sales_tax', 0)),
            "platform": request.form.get('platform'),
            "source": request.form.get('source'),
            "color": request.form.get('color', ''),
            "comments": request.form.get('comments', '')
        }
    except Exception as e:
        print(f"Invalid update payload: {e}")
        return {"success": False, "error": "Invalid payload"}, 400

    print(f"order_no1: {request.form.get('order_no')}")
    print(f"order_no2: {order['order_no']}")
    api_url = f"{sales_manager_api_url}/orders/{order['order_no']}"
    try:
        response = requests.put(api_url, json=order)
        response.raise_for_status()
        return {"success": True}, 200
    except Exception as e:
        print(f"Error updating order: {e}")
        return {"success": False, "error": str(e)}, 400

# Route to query an order by order number
@app.route('/orders/<order_no>')
def get_order(order_no):
    print(f"Fetching order {order_no}") 
    api_url = f"{sales_manager_api_url}/orders/{order_no}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        order = response.json()
        return order, 200
    except Exception as e:
        print(f"Error fetching order {order_no}: {e}")
        return {"success": False, "error": str(e)}, 404

if __name__ == "__main__":
    app.run(debug=True, port=7092)