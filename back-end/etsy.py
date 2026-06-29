import os
from typing import Any, Dict, Optional
from api_models import Receipt, Total
from token_store import load_tokens
from oauth_token import get_token_from_refresh
import requests

BASE_URL = "https://openapi.etsy.com/v3/application"
CLIENT_ID = os.getenv("ETSY_CLIENT_ID", "")
SHOP_ID = os.getenv("ETSY_SHOP_ID", "")

def get_receipt(receipt_id: int, timeout: int = 10)-> Receipt:
    """
    Fetch a single receipt from the Etsy API v3.

    - Provide an OAuth2 access token (Bearer) via access_token or ETSY_ACCESS_TOKEN env var.
    - Raises RuntimeError if no token available.
    - Returns the parsed JSON response or a dict with error info on failure.
    """
    # Load tokent from file
    tokens = load_tokens()
    print(f"Loaded Tokens: {tokens}")

    # if not tokens or not isinstance(tokens, dict):
    #     raise RuntimeError("Error loading tokens: expected a dict with access_token and refresh_token")

    refresh_token = tokens[1]
    # access_token = tokens.get('access_token')}
    # if not access_token or not refresh_token:
    #     raise RuntimeError("Missing access_token or refresh_token in tokens")

    # Optionally refresh the access token if needed (pseudo, depends on your logic)
    token = get_token_from_refresh(refresh_token)
    access_token = token.access_token

    url = f"{BASE_URL}/shops/{SHOP_ID}/receipts/{receipt_id}"
    print(f"Fetching receipt from URL: {url}")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "x-api-key": f"{CLIENT_ID}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    
        # response.raise_for_status()
        if response.status_code != 200:
            # print(f"Unexpected status code: {response.status_code}")
            return {"error": "Receipt not found"}, 404
        receipt_data = response.json()
        print(f"Grant Total: {receipt_data.get('grandtotal').get('amount')}")
        print(f"Grant Total Currency: {receipt_data.get('grandtotal').get('currency_code')}")
        return receipt_data
       
    except requests.HTTPError as exc:
        resp = getattr(exc, "response", None)
        print(f"HTTPError: {exc}, status: {getattr(resp, 'status_code', None)}")
       
    except ValueError as exc:
        print(f"ValueError: Invalid JSON response: {exc}")
        return {"error": "Invalid JSON response"}, 404
    except requests.RequestException as exc:
        print(f"RequestException: {exc}")
        return {"error": "Request failed"}, 404

if __name__ == "__main__":
    # quick manual test (set ETSY_ACCESS_TOKEN in your environment before running)
    import json
    receipt_id = 3758118341
    receipt = get_receipt(receipt_id)
    print (f"Receipt: {receipt.receipt_id}, Buyer: {receipt.name}, Total: {receipt.grant_total.amount} {receipt.grant_total.currency_code}")