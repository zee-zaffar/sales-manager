import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.etsy import get_receipt
from utils.csv_writer import open_csv_for_writing

RECEIPTS_FILE = 'utils/receipts.txt'
API_URL = 'https://api.example.com/get-receipt'  # Replace with actual API endpoint

def process_orders():
    receipts_file_path = 'utils/receipts.txt'
    orders_file_path = 'utils/etsy_orders.csv'

    # Open orders CSV file for writing
    ordersFile, ordersWriter = open_csv_for_writing(orders_file_path)

    # Read receipt IDs from text file and process each
    with open(receipts_file_path, 'r') as receiptsFile:

        # Write header row to orders CSV
        ordersWriter.writerow([
            'Order Date','Order No','Qty','Category','Color','Source','Platform','OrderAmount','SalesTax'
        ])

        # Process each receipt ID
        for line in receiptsFile:
            receipt_Id = int(line.strip())
            print(f"Receipt:{receipt_Id}")

            # Fetch receipt details from Etsy API
            receipt = get_receipt(receipt_Id)

            #if receipt exitst, write to CSV
            if receipt:
                ordersWriter.writerow([
                    receipt.create_timestamp,                   # Order Date
                    receipt.receipt_id,                         # Order No
                    receipt.transactions[0].quantity,           # Qty (may need to sum from transactions)
                    # receipt.get('category', ''),                      # Category (custom mapping may be needed)
                    # receipt.get('color', ''),                         # Color (custom mapping may be needed)
                    "Suaz-3",                                           # Source (custom mapping may be needed)
                    "Etsy",                                             # Platform (custom mapping may be needed)
                    receipt.grandtotal.amount,
                    receipt.total_tax_cost.amount                   # SalesTax
                ])
            else:
                print(f"Failed to fetch receipt from API {receipt_Id}")

        ordersFile.close() 

# def get_receipt(receipt_id:int):
#     response = requests.get(f"{API_URL}/{receipt_id}")
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Failed to fetch receipt {receipt_id}: {response.status_code}")
#         return None

def append_receipt_to_csv(receipt):
    orders_file_path = 'utils/etsy_sales.csv'

def main():
   process_orders()

if __name__ == "__main__":
    main()
