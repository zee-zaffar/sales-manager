from flask import Flask, render_template
from database.products import get_products
from database.orders import get_orders
from business.orders import process_orders
from database.shipments import get_shipments, get_shipment_header, get_shipment_details
from database.payments import get_payments_by_shipmentheader
app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)