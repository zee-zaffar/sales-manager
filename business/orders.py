import sys
import os
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.csv_writer import open_csv_for_writing
import requests
from api.models import Total, Transaction, Receipt

RECEIPTS_FILE = 'utils/receipts.txt'
API_URL = 'https://api.example.com/get-receipt'  # Replace with actual API endpoint

def process_receipts():
    receipts_file_path = 'utils/receipts.txt'
    orders_file_path = 'utils/etsy_orders.csv'

    # Open orders CSV file for writing
    ordersFile, ordersWriter = open_csv_for_writing(orders_file_path)

    # Read receipt IDs from text file and process each
    with open(receipts_file_path, 'r') as receiptsFile:

        # Write header row to orders CSV
        ordersWriter.writerow([
            'Order Date','Order No','SKU','Qty','Category','Color','Source','Platform','OrderAmount','SalesTax','Title'
        ])

        # Process each receipt ID
        for line in receiptsFile:
            receipt_Id = int(line.strip())
            print(f"Receipt:{receipt_Id}")

            # Fetch receipt details from Etsy API
            receipt = get_receipt(receipt_Id)

            #if receipt exitst, write to CSV
            if receipt:
                try:
                    order_date = datetime.datetime.fromtimestamp(receipt.create_timestamp).strftime('%m/%d/%y')
                except Exception:
                    order_date = receipt.create_timestamp  # fallback if conversion fails

                ordersWriter.writerow([
                    order_date,                                 # Order Date
                    receipt.receipt_id, 
                    receipt.transactions[0].sku,                # Sku
                    receipt.transactions[0].quantity,           # Qty (may need to sum from transactions)
                    "",
                    "",
                    "Suaz-3",                                   # Source (custom mapping may be needed)
                    "Etsy",                                     # Platform (custom mapping may be needed)
                    f"{receipt.grandtotal.amount/100:.2f}",     # OrderAmount formatted
                    f"{receipt.total_tax_cost.amount/100:.2f}",  # SalesTax formatted
                    receipt.transactions[0].title,              # Title
                ])
            else:
                print(f"Failed to fetch receipt from API {receipt_Id}")

        ordersFile.close() 
        return {"status": "completed"}

def get_receipt(receipt_id: int):
    sales_manager_api_url = os.getenv("SALES_MANAGER_API_URL", "").rstrip("/")
    try:
        response = requests.get(f"{sales_manager_api_url}/etsy/receipts/{receipt_id}")
        response.raise_for_status()
        data = response.json()
        receipt = Receipt(**data)
        # ensure grandtotal is parsed into a Total and assigned to the expected attribute name
        receipt.grandtotal = Total(**data.get("grandtotal", {}))
        receipt.transactions = [Transaction(**t) for t in data.get("transactions", [])]
        return receipt
    except Exception as e:
        print(f"Error updating order: {e}")
        return None

# def append_receipt_to_csv(receipt):
#     orders_file_path = 'utils/etsy_sales.csv'

