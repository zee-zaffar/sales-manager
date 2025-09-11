import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
load_dotenv()

import requests
from interfaces import Total, Transaction, Receipt

BASE_URL = "https://openapi.etsy.com/v3/application"


def get_receipt(receipt_id: int, access_token: Optional[str] = None, timeout: int = 10):
    """
    Fetch a single receipt from the Etsy API v3.

    - Provide an OAuth2 access token (Bearer) via access_token or ETSY_ACCESS_TOKEN env var.
    - Raises RuntimeError if no token available.
    - Returns the parsed JSON response or a dict with error info on failure.
    """
    token = access_token or os.getenv("ETSY_ACCESS_TOKEN")
    apiKey = os.getenv("ETSY_API_KEY")

    if not token:
        raise RuntimeError("ETSY_ACCESS_TOKEN environment variable not set and no access_token provided")

    url = f"{BASE_URL}/shops/38164727/receipts/{receipt_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "x-api-key": f"{apiKey}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        receipt = Receipt(**data)
        receipt.grant_total = Total(**data.get("grandtotal", {}))
        print(f"Receipt Dump:{receipt.model_dump()}")
        print(f"ReceiptId: {receipt.receipt_id}")

    except requests.HTTPError as exc:
        # HTTP error from raise_for_status(); include response info
        resp = getattr(exc, "response", None)
        return {"error": True, "exception": str(exc), "status_code": getattr(resp, "status_code", None), "text": getattr(resp, "text", None)}
    except ValueError as exc:
        # JSON decoding or validation error
        return {"error": True, "exception": f"Invalid JSON response: {exc}"}
    except requests.RequestException as exc:
        # network-level errors
        return {"error": True, "exception": str(exc), "status_code": None, "text": None}


if __name__ == "__main__":
    # quick manual test (set ETSY_ACCESS_TOKEN in your environment before running)
    import json
    receipt_id = 3758118341
    result = get_receipt(receipt_id)