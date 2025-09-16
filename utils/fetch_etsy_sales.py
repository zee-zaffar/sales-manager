import requests
import csv
from datetime import datetime

API_KEY = 'YOUR_ETSY_API_KEY'
SHOP_ID = 'YOUR_SHOP_ID'

def get_etsy_receipts():
    url = f'https://openapi.etsy.com/v2/shops/{SHOP_ID}/receipts'
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['results']

def append_receipts_to_csv(receipts, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Order Date','Order No','Qty','Category','Color','Source','Platform','OrderAmount','SalesTax'
        ])
        for r in receipts:
            writer.writerow([
                r.get('creation_tsz'),      # Order Date
                r.get('receipt_id'),        # Order No
                r.get('quantity', ''),      # Qty (may need to sum from transactions)
                r.get('category', ''),      # Category (custom mapping may be needed)
                r.get('color', ''),         # Color (custom mapping may be needed)
                r.get('source', ''),        # Source (custom mapping may be needed)
                r.get('platform', ''),      # Platform (custom mapping may be needed)
                r.get('grandtotal', ''),    # OrderAmount
                r.get('total_tax_cost', '') # SalesTax
            ])

def main():
    receipts = get_etsy_receipts()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f"utils/etsy_sales_{timestamp}.csv"
    append_receipts_to_csv(receipts, csv_file)
    print(f"Saved Etsy sales to {csv_file}")

if __name__ == '__main__':
    main()
