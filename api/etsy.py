
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from typing import Any, Dict, Optional
from access_token import get_etsy_access_token
from dotenv import load_dotenv
load_dotenv()

import requests
from interfaces import Total, Transaction, Receipt

BASE_URL = "https://openapi.etsy.com/v3/application"


def get_receipt(receipt_id: int, timeout: int = 10)-> Receipt:
    """
    Fetch a single receipt from the Etsy API v3.

    - Provide an OAuth2 access token (Bearer) via access_token or ETSY_ACCESS_TOKEN env var.
    - Raises RuntimeError if no token available.
    - Returns the parsed JSON response or a dict with error info on failure.
    """
    access_token = os.getenv("ETSY_ACCESS_TOKEN")
    client_id = os.getenv("ETSY_API_KEY")
    # access_token = get_etsy_access_token(
    #     client_id= client_id,
    #     auth_code= os.getenv("ETSY_AUTH_CODE"),
    #     code_verifier= os.getenv("ETSY_CODE_VERIFIER"),
    #     redirect_uri= os.getenv("ETSY_REDIRECT_URI")
    # )

    if not access_token:
        raise RuntimeError("Error generating access token")

    receipt: Optional[Receipt] = None
    url = f"{BASE_URL}/shops/38164727/receipts/{receipt_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "x-api-key": f"{client_id}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        receipt = Receipt(**data)
        receipt.grant_total = Total(**data.get("grandtotal", {}))
       
        return receipt

    except requests.HTTPError as exc:
        # HTTP error from raise_for_status(); include response info
        resp = getattr(exc, "response", None)
        # return {"error": True, "exception": str(exc), "status_code": getattr(resp, "status_code", None), "text": getattr(resp, "text", None)}
        return None
    except ValueError as exc:
        # JSON decoding or validation error
        # return {"error": True, "exception": f"Invalid JSON response: {exc}"}
        return None
    except requests.RequestException as exc:
        # network-level errors
        # return {"error": True, "exception": str(exc), "status_code": None, "text": None}
        return None

if __name__ == "__main__":
    # quick manual test (set ETSY_ACCESS_TOKEN in your environment before running)
    import json
    receipt_id = 3758118341
    receipt = get_receipt(receipt_id)
    print (f"Receipt: {receipt.receipt_id}, Buyer: {receipt.name}, Total: {receipt.grant_total.amount} {receipt.grant_total.currency_code}")