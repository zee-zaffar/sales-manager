from flask import Flask, render_template
from get_products import get_products

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
    return render_template("sales.html")

@app.route("/suppliers")
def suppliers():
    return render_template("suppliers.html")

if __name__ == "__main__":
    app.run(debug=True)