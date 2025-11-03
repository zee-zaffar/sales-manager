import sys
import os
import datetime

from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.csv_writer import open_csv_for_writing
import requests
from api.models import Total, Transaction, Receipt

load_dotenv()

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
            'Order Date','Order No','Status', 'SKU','Qty','Category','Color','Source','Platform','Order Amt', 'Tax', 'Gross Rev','Fee','Shipping','Net Rev','COGS','Profit','Title'
        ])

        # Process each receipt ID
        for line in receiptsFile:
            receipt_Id = int(line.strip())

            # Fetch receipt details from Etsy API
            receipt_data = get_receipt(receipt_Id)

            #if receipt exitst, write to CSV
            if not receipt_data:
                print(f"Failed to fetch receipt from API {receipt_Id}")
                continue
        
            try:
                order_date = datetime.datetime.fromtimestamp(receipt_data.create_timestamp).strftime('%m/%d/%y')
                grand_total = receipt_data.grandtotal.amount/100
                sales_tax = receipt_data.total_tax_cost.amount/100
                gross_revenue = grand_total - sales_tax
                etsy_fees = ((grand_total - sales_tax)*0.065) + ((grand_total*0.03) + 0.25)       # Example Etsy fee calculation
                net_revenue = gross_revenue - etsy_fees - 0

            except Exception:
                order_date = receipt_data.create_timestamp  # fallback if conversion fails

            ordersWriter.writerow([
            order_date,                                             # Order Date
                receipt_data.receipt_id,                            # Order No
                receipt_data.status,                                # Status
                receipt_data.transactions[0].sku,                   # Sku
                receipt_data.transactions[0].quantity,              # Qty (may need to sum from transactions)
                "",                                                 # Category (custom mapping may be needed)   
                "",                                                 # Color (custom mapping may be needed)
                "Suaz-3",                                           # Source (custom mapping may be needed)
                "Etsy",                                             # Platform (custom mapping may be needed
                f"{grand_total:.2f}",                               # Order Amount formatted
                f"{sales_tax:.2f}",                                 # Sales Tax formatted
                f"{gross_revenue:.2f}",                             # Gross Revenue                     # Net Revenue (Grand Total - Tax)
                f"{etsy_fees:.2f}",                                 # Etsy Fee
                "0",                                                # Shipping Fee placeholder
                f"{net_revenue:.2f}",                               # Net Revenue (Gross Revenue - Etsy Fees)
                "0",                                                # COGS placeholder
                "Profit",                                           # Profit placeholder
                receipt_data.transactions[0].title                  # Title
            ])
            print(f"Receipt:{receipt_Id} successfully processed")
               
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
        print(f"Error fetching receipt details: {e}")
        return None

if __name__ == "__main__":
    process_receipts()

