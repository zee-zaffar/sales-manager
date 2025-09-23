
import os
import sys
from flask import Flask, flash, redirect, render_template, request, url_for
from database.products import get_products
from database.orders import get_orders
from business.orders import process_orders
from database.payments import get_payments_by_shipmentheader, add_payment
import requests

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # Change this to a strong, random value in production

sales_manager_api_url = os.getenv("SALES_MANAGER_API_URL")
print(f"Sales Manager API URL: {sales_manager_api_url}")
@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/inventory")
# def inventory():
#     return render_template("inventory.html")

@app.route("/products")
def products():
    try:
        response = requests.get(f"{sales_manager_api_url}/products")
        response.raise_for_status()
        products = response.json()
        print(f"Products fetched: {products}")
    except Exception as e:
        print(f"Error fetching products: {e}")
       
    return render_template("products_list.html", products = products)

@app.route("/sales")
def sales():
    # Process receipts from file and fetch details
    process_orders()
     
    # print(f"Orders fetched: {get_orders()}")
    return render_template("sales.html", orders = get_orders())

@app.route("/suppliers")
def suppliers():
    return render_template("suppliers.html")

# Get all shipments
@app.route("/shipments")
def shipments():
    try:
        response = requests.get(f"{sales_manager_api_url}/shipments")
        response.raise_for_status()
        shipments = response.json()
    except Exception as e:
        print(f"Error fetching shipments: {e}")
        # shipments = []
    return render_template("shipments_list.html", shipments=shipments)

# Get a single shipment header with associated details and payments
@app.route("/shipment/<int:shipment_id>")
def shipment_details(shipment_id):

    response = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}")
    response.raise_for_status()
    shipment = response.json()

    response2 = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}/details")
    response2.raise_for_status()
    
    details = response2.json()
    print(f"Shipment Details: {details}")

    payments =   response = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}/payments")
    response.raise_for_status()
    payments = response.json()
    
    return render_template('shipment_details.html', shipment=shipment, details=details, payments=payments)

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
    print (f"Payload: {payload}")
           
    # Send POST request to API
    api_url = f"{sales_manager_api_url}/shipments"
    response = requests.post(api_url, json=payload)
    if response.status_code == 201:
        flash('Shipment added successfully!')
    else:
        flash('Failed to add shipment.')
    return redirect(url_for('shipments'))

# Route to add new payment form
@app.route('/shipment/<int:shipment_id>/payment/new')
def new_payment(shipment_id):
    return render_template('payment_entry.html', shipment_id=shipment_id)

# Route to handle payment form submission
# @app.route('/shipment/<int:shipment_id>/payment/new', methods=['POST'])
# def submit_payment(shipment_id):
#     paymentdate = request.form.get('paymentdate')
#     description = request.form.get('description')
#     amount = request.form.get('amount')
#     fee = request.form.get('fee')
#     comments = request.form.get('comments')
#     add_payment(shipment_id, paymentdate, description, amount, fee, comments)
#     flash('Payment added successfully!')
#     return redirect(url_for('shipment_details', shipment_id=shipment_id))

# New route to handle payment form submission
@app.route('/shipments/<int:shipment_id>/payments/add', methods=['POST'])
def add_payment_modal(shipment_id):
    paymentdate = request.form.get('PaymentDate')
    description = request.form.get('Description')
    amount = request.form.get('Amount')
    fee = request.form.get('Fee')
    comments = request.form.get('Comments')
    add_payment(shipment_id, paymentdate, description, amount, fee, comments)
    flash('Payment added successfully!')
    return redirect(url_for('shipment_details', shipment_id=shipment_id))

# Add new shipment detail form submit
@app.route('/shipments/<int:shipment_header_id>/details/add', methods=['POST'])
def add_detail_modal(shipment_header_id):
    shipment_detail = {
        "Description" : request.form.get('Description'),
        "SKU": request.form.get('SKU'),
        "Quantity": request.form.get('Quantity'),
        "UnitPrice": request.form.get('UnitPrice'),
        "Comments": request.form.get('Comments')
    }

    api_url = f"{sales_manager_api_url}/shipments/{shipment_header_id}/details"
    response = requests.post(api_url, json=shipment_detail)
    if response.status_code == 201:
        flash('Shipment details added successfully!')
    else:
        flash('Failed to add shipment details.')


    return redirect(url_for('shipments'))

# Route to handle new product form submission
@app.route('/products/new', methods=['POST'])
def add_product():
    # Map form fields to API fields
    product = {
        "productcode": request.form.get('code'),
        "productcategory": request.form.get('category'),
        "productcost": float(request.form.get('cost', 0)),
        "productdesc": request.form.get('description'),
        "color": request.form.get('color', ''),
        "comments": request.form.get('comments', '')
    }
    api_url = f"{sales_manager_api_url}/products"
  
    response = requests.post(api_url, json=product)
    response.raise_for_status()
    return {"success": True}, 201
  

if __name__ == "__main__":
    app.run(debug=True)