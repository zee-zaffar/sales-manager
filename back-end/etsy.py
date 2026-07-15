import os
import calendar
from datetime import datetime, timezone
from typing import Any, Dict, List
from api_models import Receipt, Total
from token_store import load_tokens
from oauth_token import get_token_from_refresh
import requests

BASE_URL = "https://openapi.etsy.com/v3/application"
CLIENT_ID = os.getenv("ETSY_CLIENT_ID", "")
SHOP_ID = os.getenv("ETSY_SHOP_ID", "")

def _auth_headers() -> Dict[str, str]:
    _, refresh_token = load_tokens()
    token = get_token_from_refresh(refresh_token)
    if not token or not getattr(token, "access_token", None):
        raise RuntimeError(
            "Could not refresh Etsy access token. The ETSY_CLIENT_ID / refresh "
            "token is likely invalid or inactive — check the app in Etsy's "
            "developer console (etsy.com/developers/your-apps)."
        )
    return {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
        "x-api-key": CLIENT_ID
    }

def get_receipt(receipt_id: int, timeout: int = 10)-> Receipt:
    """
    Fetch a single receipt from the Etsy API v3.
    """
    url = f"{BASE_URL}/shops/{SHOP_ID}/receipts/{receipt_id}"
    print(f"Fetching receipt from URL: {url}")

    try:
        response = requests.get(url, headers=_auth_headers(), timeout=timeout)

        if response.status_code != 200:
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

def _money(value: Dict[str, Any]) -> float:
    if not value:
        return 0.0
    amount = value.get("amount", 0) or 0
    divisor = value.get("divisor") or 100
    return amount / divisor

def _simplify_receipt(receipt: Dict[str, Any]) -> Dict[str, Any]:
    transactions = receipt.get("transactions") or []
    line_items = [
        {
            "title": t.get("title"),
            "sku": t.get("sku") or None,
            "quantity": t.get("quantity") or 0,
        }
        for t in transactions
    ]
    total_qty = sum(li["quantity"] for li in line_items) or 1
    create_ts = receipt.get("create_timestamp")
    order_date = (
        datetime.fromtimestamp(create_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        if create_ts else None
    )
    first = line_items[0] if line_items else {}

    return {
        "order_no": str(receipt.get("receipt_id")),
        "order_date": order_date,
        "order_amount": round(_money(receipt.get("grandtotal")), 2),
        "sales_tax": round(_money(receipt.get("total_tax_cost")), 2),
        "qty": total_qty,
        "sku": first.get("sku"),
        "source": first.get("title"),
        "platform": "Etsy",
        "multi_item": len(line_items) > 1,
        "line_items": line_items,
    }

def get_receipts_for_shop(min_created: int, max_created: int, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch every receipt for the shop created within [min_created, max_created]
    (unix timestamps), paging through Etsy's results.
    """
    headers = _auth_headers()
    url = f"{BASE_URL}/shops/{SHOP_ID}/receipts"
    limit = 100
    offset = 0
    results: List[Dict[str, Any]] = []

    while True:
        params = {
            "min_created": min_created,
            "max_created": max_created,
            "limit": limit,
            "offset": offset,
        }
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        if response.status_code != 200:
            raise RuntimeError(f"Etsy API error {response.status_code}: {response.text}")

        data = response.json()
        batch = data.get("results") or []
        results.extend(batch)

        if len(batch) < limit:
            break
        offset += limit

    return results

def get_receipts_for_month(year: int, month: int) -> List[Dict[str, Any]]:
    """Fetch and simplify all receipts created in the given calendar month (UTC)."""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    receipts = get_receipts_for_shop(int(start.timestamp()), int(end.timestamp()))
    return [_simplify_receipt(r) for r in receipts]

if __name__ == "__main__":
    # quick manual test (set ETSY_ACCESS_TOKEN in your environment before running)
    import json
    receipt_id = 3758118341
    receipt = get_receipt(receipt_id)
    print (f"Receipt: {receipt.receipt_id}, Buyer: {receipt.name}, Total: {receipt.grant_total.amount} {receipt.grant_total.currency_code}")
