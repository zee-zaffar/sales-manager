from flask import Flask, flash, redirect, render_template, request, url_for
from database.products import get_products
from database.orders import get_orders
from business.orders import process_orders
from database.shipments import get_shipments, get_shipment_header, get_shipment_details, add_shipment_header, add_shipment_detail
from database.payments import get_payments_by_shipmentheader, add_payment
app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # Change this to a strong, random value in production

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

@app.route("/products")
def products():
    print(f"Products fetched: {get_products()}")
    return render_template("products.html", products = get_products())

@app.route("/sales")
def sales():
    # Process receipts from file and fetch details
    process_orders()
     
    # print(f"Orders fetched: {get_orders()}")
    return render_template("sales.html", orders = get_orders())

@app.route("/suppliers")
def suppliers():
    return render_template("suppliers.html")

@app.route("/shipments")
def shipments():
    return render_template("shipments_list.html", shipments = get_shipments())

@app.route("/shipment/<int:shipment_id>")
def shipment_details(shipment_id):
    shipment = get_shipment_header(shipment_id)
    details = get_shipment_details(shipment_id)
    payments = get_payments_by_shipmentheader(shipment_id)
    
    return render_template('shipment_details.html', shipment=shipment, details=details, payments=payments)

@app.route('/shipment/new')
def new_shipment():
    return render_template('shipment_entry.html')

# Route to handle form submission for new shipment
@app.route('/shipment/new', methods=['POST'])
def submit_shipment():
    # Get header fields
    supplier_name = request.form.get('supplier_name')
    shipment_no = request.form.get('shipment_no')
    date_received = request.form.get('date_received')
    comments = request.form.get('comments')

    # Insert header and get ID
    header_id = add_shipment_header(supplier_name, shipment_no, date_received, comments)

    # Get details (multiple rows)
    descriptions = request.form.getlist('description[]')
    skus = request.form.getlist('sku[]')
    quantities = request.form.getlist('quantity[]')
    unit_prices = request.form.getlist('unit_price[]')
    detail_comments = request.form.getlist('detail_comments[]')

    for desc, sku, qty, price, comm in zip(descriptions, skus, quantities, unit_prices, detail_comments):
        add_shipment_detail(
            header_id=header_id,
            description=desc,
            sku=sku,
            quantity=int(qty),
            unit_price=float(price),
            comments=comm
        )

    flash('Shipment added successfully!')
    return redirect(url_for('shipments_list'))

@app.route('/shipment/<int:shipment_id>/payment/new')
def new_payment(shipment_id):
    return render_template('payment_entry.html', shipment_id=shipment_id)

# Route to handle payment form submission
@app.route('/shipment/<int:shipment_id>/payment/new', methods=['POST'])
def submit_payment(shipment_id):
    paymentdate = request.form.get('paymentdate')
    description = request.form.get('description')
    amount = request.form.get('amount')
    fee = request.form.get('fee')
    comments = request.form.get('comments')
    add_payment(shipment_id, paymentdate, description, amount, fee, comments)
    flash('Payment added successfully!')
    return redirect(url_for('shipment_details', shipment_id=shipment_id))

if __name__ == "__main__":
    app.run(debug=True)