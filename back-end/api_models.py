from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class Transaction(BaseModel):
    transaction_id: Optional[int]
    listing_id: Optional[int]
    title: Optional[str]
    quantity: Optional[int]
    sku: Optional[str]

    class Config:
        extra = "allow"

class Total(BaseModel):
    amount: Optional[int]
    currency_code: Optional[str]

    class Config:
        extra = "allow"

class Receipt(BaseModel):
    receipt_id: Optional[int]
    seller_email: Optional[str]
    grandtotal: Optional[Total]
    subtotal: Optional[Total]
    total_price: Optional[Total]
    total_tax_cost: Optional[Total]
    create_timestamp: Optional[int]
    transactions: Optional[List[Transaction]]

    class Config:
        extra = "allow"

class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

    class Config:
        extra = "allow"