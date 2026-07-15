
import os
import base64
import json
from flask import Flask, Response, flash, redirect, render_template, request, url_for
import requests
from dotenv import load_dotenv
import anthropic
# from api.oauth_token import get_refresh_token
from business.orders import process_receipts

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-very-secret-key")  # Change this to a strong, random value in production

sales_manager_api_url = os.getenv("SALES_MANAGER_API_URL", "").rstrip("/")
    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inventory")
def inventory():
    inventory = []
    try:
        response = requests.get(f"{sales_manager_api_url}/inventory")
        response.raise_for_status()
        inventory = response.json()
    except Exception as e:
        print(f"Error fetching inventory: {e}")
    return render_template("inventory.html", inventory=inventory)

@app.route("/products")
def products():
    products = []
    try:
        response = requests.get(f"{sales_manager_api_url}/products")
        response.raise_for_status()
        products = response.json()
        
    except Exception as e:
        print(f"Error fetching products: {e}")
       
    return render_template("products_list.html", products = products)

# Toggle a product's active status
@app.route('/products/<code>/active', methods=['POST'])
def update_product_active_modal(code):
    try:
        response = requests.put(
            f"{sales_manager_api_url}/products/{code}/active",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Update a product
@app.route('/products/<code>/update', methods=['POST'])
def update_product_modal(code):
    try:
        response = requests.put(
            f"{sales_manager_api_url}/products/{code}",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Delete a product
@app.route('/products/<code>', methods=['DELETE'])
def delete_product_modal(code):
    try:
        response = requests.delete(f"{sales_manager_api_url}/products/{code}")
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/process_receipts")
def get_receipts():
    # Process Etsy receipts from utils\receipts.txt file
    return process_receipts()

@app.route("/suppliers")
def suppliers():
    suppliers = []
    try:
        response = requests.get(f"{sales_manager_api_url}/suppliers")
        response.raise_for_status()
        suppliers = response.json()
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
    return render_template("suppliers.html", suppliers=suppliers)

@app.route("/suppliers/new", methods=["POST"])
def supplier_add():
    try:
        response = requests.post(f"{sales_manager_api_url}/suppliers", json=request.get_json())
        response.raise_for_status()
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/suppliers/<int:supplier_id>", methods=["PUT"])
def supplier_update(supplier_id):
    try:
        response = requests.put(f"{sales_manager_api_url}/suppliers/{supplier_id}", json=request.get_json())
        response.raise_for_status()
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

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
    invoices = []
    active_products = []
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

        response4 = requests.get(f"{sales_manager_api_url}/shipments/{shipment_id}/invoices")
        response4.raise_for_status()
        invoices = response4.json()

        response5 = requests.get(f"{sales_manager_api_url}/products", params={"active_only": "true"})
        response5.raise_for_status()
        active_products = response5.json()
    except Exception as e:
        print(f"Error fetching shipment details/payments/invoices: {e}")

    details_grand_total = sum(
        d['quantity'] * (d['landed_cost'] if d['landed_cost'] is not None else d['unit_price'])
        for d in details
    )
    payments_grand_total = sum(p['amount'] + p['fee'] for p in payments)
    invoices_grand_total = sum(i['amount'] for i in invoices)
    return render_template(
        'shipment_details.html',
        shipment=shipment,
        details=details,
        payments=payments,
        invoices=invoices,
        active_products=active_products,
        details_grand_total=details_grand_total,
        payments_grand_total=payments_grand_total,
        invoices_grand_total=invoices_grand_total
    )

# Update shipment header
@app.route('/shipments/<int:shipment_id>/update', methods=['POST'])
def update_shipment_header_modal(shipment_id):
    try:
        response = requests.put(
            f"{sales_manager_api_url}/shipments/{shipment_id}",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

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
            "description": desc,
            "sku": sku,
            "quantity": int(qty),
            "unit_price": float(price),
            "comments": comm
        })

    # Prepare payload for API
    payload = {
        "supplier_name": supplier_name,
        "shipment_no": shipment_no,
        "date_received": date_received,
        "comments": comments,
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

# Update shipment detail
@app.route('/shipments/<int:header_id>/details/update', methods=['POST'])
def update_detail_modal(header_id):
    data = request.get_json()
    detail_id = data.pop('detail_id', None)
    try:
        response = requests.put(
            f"{sales_manager_api_url}/shipments/{header_id}/details/{detail_id}",
            json=data
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Update payment
@app.route('/shipments/<int:header_id>/payments/update', methods=['POST'])
def update_payment_modal(header_id):
    data = request.get_json()
    payment_id = data.pop('payment_id', None)
    try:
        response = requests.put(
            f"{sales_manager_api_url}/shipments/{header_id}/payments/{payment_id}",
            json=data
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Add new payment
@app.route('/shipments/<int:shipment_header_id>/payments/add', methods=['POST'])
def add_payment_modal(shipment_header_id):
    try:
        response = requests.post(
            f"{sales_manager_api_url}/shipments/{shipment_header_id}/payments",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Add new shipment detail
@app.route('/shipments/<int:shipment_header_id>/details/add', methods=['POST'])
def add_detail_modal(shipment_header_id):
    try:
        response = requests.post(
            f"{sales_manager_api_url}/shipments/{shipment_header_id}/details",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Bulk-upload shipment details from a CSV
@app.route('/shipments/<int:shipment_header_id>/details/bulk-upload', methods=['POST'])
def bulk_upload_details_modal(shipment_header_id):
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    f = request.files['file']
    try:
        response = requests.post(
            f"{sales_manager_api_url}/shipments/{shipment_header_id}/details/bulk-upload",
            files={'file': (f.filename, f.stream, f.content_type)}
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Download a blank CSV template for bulk shipment detail upload
@app.route('/shipments/detail-template.csv')
def shipment_detail_template():
    csv_content = "SKU,Description,Qty,Unit Price,Landed Cost,Comments\n"
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=shipment_detail_template.csv'}
    )

# Add new invoice
@app.route('/shipments/<int:shipment_header_id>/invoices/add', methods=['POST'])
def add_invoice_modal(shipment_header_id):
    try:
        response = requests.post(
            f"{sales_manager_api_url}/shipments/{shipment_header_id}/invoices",
            json=request.get_json()
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Update invoice
@app.route('/shipments/<int:header_id>/invoices/update', methods=['POST'])
def update_invoice_modal(header_id):
    data = request.get_json()
    invoice_id = data.pop('invoice_id', None)
    try:
        response = requests.put(
            f"{sales_manager_api_url}/shipments/{header_id}/invoices/{invoice_id}",
            json=data
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Delete invoice
@app.route('/shipments/<int:header_id>/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice_modal(header_id, invoice_id):
    try:
        response = requests.delete(
            f"{sales_manager_api_url}/shipments/{header_id}/invoices/{invoice_id}"
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Delete payment
@app.route('/shipments/<int:header_id>/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment_modal(header_id, payment_id):
    try:
        response = requests.delete(
            f"{sales_manager_api_url}/shipments/{header_id}/payments/{payment_id}"
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Route to handle new product form submission
@app.route('/products/new', methods=['POST'])
def add_product():
    # Map form fields to API fields
    try:
        product = {
            "code": request.form.get('code'),
            "category": request.form.get('category'),
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
    skus = []
    try:
        response = requests.get(f"{sales_manager_api_url}/orders")
        response.raise_for_status()
        orders = response.json()

        # Sourced from inventory (SKUs actually received via shipments), not
        # just the products catalog, since a SKU may be received before it's
        # ever added as a formal product record.
        response2 = requests.get(f"{sales_manager_api_url}/inventory")
        response2.raise_for_status()
        skus = response2.json()
    except Exception as e:
        print(f"Error fetching orders: {e}")
    return render_template("orders.html", orders=orders, skus=skus)

# Monthly profit summary
@app.route('/orders/monthly-summary', methods=['GET'])
def orders_monthly_summary():
    try:
        response = requests.get(f"{sales_manager_api_url}/orders/monthly-summary")
        response.raise_for_status()
        return response.json(), 200
    except Exception as e:
        return {"error": str(e)}, 500

# Fetch a month's Etsy receipts for review, flagging ones already imported
@app.route('/orders/etsy-sync', methods=['GET'])
def orders_etsy_sync():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return {"error": "year and month are required"}, 400

    try:
        response = requests.get(
            f"{sales_manager_api_url}/etsy/receipts",
            params={"year": year, "month": month}
        )
        if not response.ok:
            return response.json(), response.status_code
        receipts = response.json()

        orders_response = requests.get(f"{sales_manager_api_url}/orders")
        orders_response.raise_for_status()
        existing_order_nos = {o['order_no'] for o in orders_response.json()}

        for r in receipts:
            r['already_imported'] = r['order_no'] in existing_order_nos

        return {"receipts": receipts}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# Import a single reviewed Etsy order into the orders table
@app.route('/orders/import', methods=['POST'])
def orders_import():
    try:
        response = requests.post(f"{sales_manager_api_url}/orders", json=request.get_json())
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Route to add a new order
@app.route('/add_order', methods=['POST'])
def add_order():
    try:
        order = {
            "order_no":      request.form.get('order_no'),
            "order_date":    request.form.get('order_date'),
            "order_amount":  float(request.form.get('order_amount', 0)),
            "qty":           int(request.form.get('qty', 0)),
            "sku":           request.form.get('sku') or None,
            "sales_tax":     float(request.form.get('sales_tax', 0)),
            "cost_of_goods": float(request.form.get('cost_of_goods', 0)),
            "shipping_cost": float(request.form.get('shipping_cost', 0)),
            "platform_fee":  float(request.form.get('platform_fee', 0)),
            "platform":      request.form.get('platform'),
            "source":        request.form.get('source'),
            "color":         request.form.get('color', ''),
            "comments":      request.form.get('comments', '')
        }
    except Exception as e:
        print(f"Invalid order payload: {e}")
        return {"success": False, "error": "Invalid payload"}, 400

    try:
        backend_response = requests.post(f"{sales_manager_api_url}/orders", json=order)
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
            "order_no":      request.form.get('order_no'),
            "order_date":    request.form.get('order_date'),
            "order_amount":  float(request.form.get('order_amount', 0)),
            "qty":           int(request.form.get('qty', 0)),
            "sku":           request.form.get('sku') or None,
            "sales_tax":     float(request.form.get('sales_tax', 0)),
            "cost_of_goods": float(request.form.get('cost_of_goods', 0)),
            "shipping_cost": float(request.form.get('shipping_cost', 0)),
            "platform_fee":  float(request.form.get('platform_fee', 0)),
            "platform":      request.form.get('platform'),
            "source":        request.form.get('source'),
            "color":         request.form.get('color', ''),
            "comments":      request.form.get('comments', '')
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

# Parse order details from an uploaded screenshot using Claude vision
@app.route('/orders/parse-screenshot', methods=['POST'])
def parse_order_screenshot():
    if 'screenshot' not in request.files:
        return {"error": "No file uploaded"}, 400
    f = request.files['screenshot']
    if not f.filename:
        return {"error": "Empty file"}, 400

    raw = f.read()
    media_type = f.content_type or 'image/png'
    if not media_type.startswith('image/'):
        return {"error": "File must be an image"}, 400

    image_b64 = base64.standard_b64encode(raw).decode('utf-8')

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not configured"}, 500

    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Extract order details from this ecommerce order screenshot (Etsy, eBay, or Facebook Marketplace).\n"
        "Return ONLY a JSON object with these exact fields (use null for fields not found):\n"
        "{\n"
        '  "order_no": "order number or transaction ID",\n'
        '  "order_date": "YYYY-MM-DD",\n'
        '  "order_amount": 0.00,\n'
        '  "qty": 1,\n'
        '  "sales_tax": 0.00,\n'
        '  "platform": "Etsy" or "eBay" or "Facebook" or "Other",\n'
        '  "source": "listing title or item name",\n'
        '  "color": "color or variant if visible or null"\n'
        "}\n"
        "Return only the JSON — no explanation, no markdown fences."
    )
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
    except Exception as e:
        return {"error": f"Claude API error: {str(e)}"}, 500

    text = message.content[0].text.strip()
    # Strip accidental markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1].lstrip("json").strip() if len(parts) > 1 else text
    try:
        parsed = json.loads(text)
        return {"success": True, "order": parsed}, 200
    except Exception:
        return {"error": "Could not parse extracted data", "raw": text}, 500

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