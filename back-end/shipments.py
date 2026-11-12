import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import jsonify
from sqlalchemy import func

from db_models import ShipmentHeader, ShipmentDetail, Payment, Invoice, Products
from main import db

INVOICE_TYPES = ('product', 'shipping', 'customs', 'other')


# ---------------------------------------------------------------------------
# Errors + validation helpers
# ---------------------------------------------------------------------------

class ApiError(Exception):
    """Raised for any client-correctable problem; rendered as JSON by routes.py."""

    def __init__(self, message, status=400, error=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.error = error or {400: 'Validation error', 404: 'Not found', 409: 'Conflict'}.get(status, 'Error')


def _body(data):
    if not isinstance(data, dict):
        raise ApiError('Request body must be a JSON object')
    return data


def _text(data, field, required=False, max_len=None):
    v = data.get(field)
    v = v.strip() if isinstance(v, str) else v
    if v in (None, ''):
        if required:
            raise ApiError(f'{field} is required')
        return None
    if not isinstance(v, str):
        v = str(v)
    if max_len and len(v) > max_len:
        raise ApiError(f'{field} must be at most {max_len} characters')
    return v


def _date(data, field, required=False):
    v = data.get(field)
    if v in (None, ''):
        if required:
            raise ApiError(f'{field} is required')
        return None
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v).strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ApiError(f'{field} must be a valid date in YYYY-MM-DD format')


def _int(data, field, required=False, minimum=None):
    v = data.get(field)
    if v in (None, ''):
        if required:
            raise ApiError(f'{field} is required')
        return None
    try:
        d = Decimal(str(v).strip())
        if d != d.to_integral_value():
            raise ValueError
        n = int(d)
    except (InvalidOperation, ValueError):
        raise ApiError(f'{field} must be a whole number')
    if minimum is not None and n < minimum:
        raise ApiError(f'{field} must be at least {minimum}')
    return n


def _money(data, field, required=False, minimum=Decimal('0'), exclusive=False, default=None):
    v = data.get(field)
    if v in (None, ''):
        if default is not None:
            return default
        if required:
            raise ApiError(f'{field} is required')
        return None
    try:
        d = Decimal(str(v).strip())
        if not d.is_finite():
            raise InvalidOperation
    except InvalidOperation:
        raise ApiError(f'{field} must be a number')
    d = d.quantize(Decimal('0.01'))
    if d >= Decimal('1e16'):
        raise ApiError(f'{field} is too large')
    if minimum is not None:
        if exclusive and d <= minimum:
            raise ApiError(f'{field} must be greater than {minimum}')
        if not exclusive and d < minimum:
            raise ApiError(f'{field} must be {minimum} or more')
    return d


def _require_shipment(shipment_header_id):
    header = db.session.get(ShipmentHeader, shipment_header_id)
    if not header:
        raise ApiError(f'No shipment found with ID {shipment_header_id}', 404)
    return header


def _get_child(model, child_id, shipment_header_id, label):
    """Fetch a detail/invoice/payment and confirm it belongs to the shipment in the URL."""
    obj = db.session.get(model, child_id)
    if not obj or (shipment_header_id is not None and obj.shipment_header_id != shipment_header_id):
        where = f' on shipment {shipment_header_id}' if shipment_header_id is not None else ''
        raise ApiError(f'No {label} found with ID {child_id}{where}', 404)
    return obj


def _paid_on_invoice(invoice_id, exclude_payment_id=None):
    q = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.invoice_id == invoice_id)
    if exclude_payment_id is not None:
        q = q.filter(Payment.id != exclude_payment_id)
    return Decimal(q.scalar())


def _check_shipment_unique(supplier_name, shipment_no, exclude_id=None):
    q = ShipmentHeader.query.filter(
        func.lower(ShipmentHeader.supplier_name) == supplier_name.lower(),
        func.lower(ShipmentHeader.shipment_no) == shipment_no.lower(),
    )
    if exclude_id is not None:
        q = q.filter(ShipmentHeader.id != exclude_id)
    if q.first():
        raise ApiError(f"Shipment '{shipment_no}' already exists for supplier '{supplier_name}'", 409)


def _check_invoice_unique(shipment_header_id, vendor_name, invoice_no, exclude_id=None):
    if not invoice_no:
        return
    q = Invoice.query.filter(
        Invoice.shipment_header_id == shipment_header_id,
        func.lower(Invoice.vendor_name) == vendor_name.lower(),
        func.lower(Invoice.invoice_no) == invoice_no.lower(),
    )
    if exclude_id is not None:
        q = q.filter(Invoice.id != exclude_id)
    if q.first():
        raise ApiError(f"Invoice '{invoice_no}' from vendor '{vendor_name}' already exists on this shipment", 409)


# --- field parsers (validate only; no DB writes) ---

def _parse_header(data):
    data = _body(data)
    return {
        'supplier_name': _text(data, 'supplier_name', required=True, max_len=255),
        'shipment_no': _text(data, 'shipment_no', required=True, max_len=100),
        'date_received': _date(data, 'date_received', required=True),
        'comments': _text(data, 'comments'),
    }


def _parse_detail(data):
    data = _body(data)
    description = _text(data, 'description')
    sku = _text(data, 'sku', max_len=100)
    if not description and not sku:
        raise ApiError('A shipment line needs a description or a sku')
    return {
        'description': description,
        'sku': sku,
        'quantity': _int(data, 'quantity', required=True, minimum=1),
        'unit_price': _money(data, 'unit_price', required=True),
        # 0 / blank means "not entered" (falls back to unit_price), as before
        'landed_cost': _money(data, 'landed_cost') or None,
        'comments': _text(data, 'comments'),
    }


def _parse_invoice(data, current_type='product'):
    data = _body(data)
    invoice_type = _text(data, 'invoice_type') or current_type
    if invoice_type not in INVOICE_TYPES:
        raise ApiError(f"invoice_type must be one of: {', '.join(INVOICE_TYPES)}")
    return {
        'vendor_name': _text(data, 'vendor_name', required=True, max_len=255),
        'invoice_no': _text(data, 'invoice_no', max_len=100),
        'invoice_date': _date(data, 'invoice_date'),
        'amount': _money(data, 'amount', required=True, exclusive=True),
        'invoice_type': invoice_type,
        'comments': _text(data, 'comments'),
    }


def _parse_payment(data):
    data = _body(data)
    return {
        'invoice_id': _int(data, 'invoice_id', minimum=1),
        'payment_date': _date(data, 'payment_date', required=True),
        'description': _text(data, 'description', required=True, max_len=100),
        'amount': _money(data, 'amount', required=True, exclusive=True),
        'fee': _money(data, 'fee', default=Decimal('0.00')),
        'comments': _text(data, 'comments'),
    }


def _check_payment_invoice(shipment_header_id, p, exclude_payment_id=None, old_amount=None):
    """Invoice must exist on the same shipment, and payments may not exceed it."""
    if not p['invoice_id']:
        return
    invoice = db.session.get(Invoice, p['invoice_id'])
    if not invoice:
        raise ApiError(f"No invoice found with ID {p['invoice_id']}", 404)
    if invoice.shipment_header_id != shipment_header_id:
        raise ApiError('Invoice belongs to a different shipment')
    already_paid = _paid_on_invoice(invoice.id, exclude_payment_id)
    new_total = already_paid + p['amount']
    # Allow an edit that does not make an already over-paid invoice any worse.
    worsens = old_amount is None or p['amount'] > Decimal(old_amount)
    if new_total > invoice.amount and worsens:
        raise ApiError(
            f"Payment would exceed invoice amount: invoice {invoice.amount}, "
            f"already paid {already_paid}, this payment {p['amount']}",
            409,
        )


# ---------------------------------------------------------------------------
# Shipment header
# ---------------------------------------------------------------------------

def _header_json(s):
    return {
        'id': s.id,
        'supplier_name': s.supplier_name,
        'shipment_no': s.shipment_no,
        'date_received': s.date_received.isoformat() if s.date_received else None,
        'comments': s.comments,
    }


def get_all_shipments_header():
    return jsonify([_header_json(p) for p in ShipmentHeader.query.all()])


def get_shipment_by_header_id(shipment_header_id):
    s = ShipmentHeader.query.get_or_404(shipment_header_id)
    return jsonify(_header_json(s))


def edit_shipment_header(shipment_header_id: int, data):
    header = _require_shipment(shipment_header_id)
    h = _parse_header(data)
    _check_shipment_unique(h['supplier_name'], h['shipment_no'], exclude_id=header.id)

    for k, v in h.items():
        setattr(header, k, v)
    db.session.commit()

    return {
        "success": True,
        "message": "Shipment updated successfully",
        "data": _header_json(header),
    }, 200


def add_shipment_header(data, commit=True) -> int:
    """Validate and add a header. With commit=False the row is only flushed so the
    caller can add details and commit everything as one transaction."""
    h = _parse_header(data)
    _check_shipment_unique(h['supplier_name'], h['shipment_no'])
    shipment = ShipmentHeader(**h)
    db.session.add(shipment)
    if commit:
        db.session.commit()
    else:
        db.session.flush()
    return shipment.id


def create_shipment_with_details(payload):
    """Create a header and all its detail lines atomically: either everything is
    saved or nothing is."""
    payload = _body(payload)
    raw_details = payload.get('Details')
    if raw_details is None:
        raw_details = []
    if not isinstance(raw_details, list):
        raise ApiError('Details must be a list')

    # Validate every line up front so a bad row never leaves a partial shipment.
    parsed = []
    for i, d in enumerate(raw_details, start=1):
        try:
            parsed.append(_parse_detail(d))
        except ApiError as e:
            raise ApiError(f'Detail line {i}: {e.message}', e.status)

    try:
        shipment_id = add_shipment_header(payload, commit=False)
        for d in parsed:
            db.session.add(ShipmentDetail(shipment_header_id=shipment_id, **d))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return shipment_id


# ---------------------------------------------------------------------------
# Shipment details
# ---------------------------------------------------------------------------

def _detail_json(d):
    return {
        'id': d.id,
        'shipment_header_id': d.shipment_header_id,
        'description': d.description,
        'sku': d.sku,
        'quantity': d.quantity,
        'unit_price': float(d.unit_price) if d.unit_price is not None else None,
        'landed_cost': float(d.landed_cost) if d.landed_cost is not None else None,
        'comments': d.comments,
    }


def get_shipment_details(shipment_header_id):
    details = ShipmentDetail.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(ShipmentDetail.description.asc()).all()
    return jsonify([_detail_json(d) for d in details])


def add_new_shipment_detail(shipment_header_id, detail):
    _require_shipment(shipment_header_id)
    new_detail = ShipmentDetail(shipment_header_id=shipment_header_id, **_parse_detail(detail))
    db.session.add(new_detail)
    db.session.commit()
    return new_detail.id


BULK_UPLOAD_COLUMNS = ['sku', 'description', 'qty', 'unit_price', 'landed_cost', 'comments']


def bulk_add_shipment_details(shipment_header_id, file_stream):
    """
    Parse a CSV of shipment detail rows (columns: sku, description, qty,
    unit_price, landed_cost, comments — header names case-insensitive, spaces
    treated as underscores) and insert them against the given shipment.
    Valid rows are inserted in one transaction; invalid rows are reported in
    'errors' and skipped. Any sku not found in the products catalog is left
    blank rather than rejecting the row. landed_cost is taken as entered.
    """
    _require_shipment(shipment_header_id)

    try:
        text = file_stream.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        raise ApiError('File must be a UTF-8 encoded CSV')
    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [(h or '').strip().lower().replace(' ', '_') for h in (reader.fieldnames or [])]
    if not reader.fieldnames or not ({'qty', 'quantity'} & set(reader.fieldnames)) or 'unit_price' not in reader.fieldnames:
        raise ApiError('CSV must have a header row with at least: qty (or quantity) and unit_price')

    known_codes = {p.code for p in Products.query.all()}

    inserted = 0
    unmatched_skus = []
    errors = []

    for row_num, row in enumerate(reader, start=2):
        if not any((v or '').strip() for v in row.values() if isinstance(v, str)):
            continue  # blank line
        data = {
            'sku': row.get('sku'),
            'description': row.get('description'),
            'quantity': row.get('qty') or row.get('quantity'),
            'unit_price': row.get('unit_price'),
            'landed_cost': row.get('landed_cost'),
            'comments': row.get('comments'),
        }
        try:
            parsed = _parse_detail(data)
        except ApiError as e:
            errors.append(f"Row {row_num}: {e.message}")
            continue

        if parsed['sku'] and parsed['sku'] not in known_codes:
            unmatched_skus.append({'row': row_num, 'sku': parsed['sku'], 'description': parsed['description']})
            parsed['sku'] = None

        db.session.add(ShipmentDetail(shipment_header_id=shipment_header_id, **parsed))
        inserted += 1

    db.session.commit()

    return {
        'inserted': inserted,
        'unmatched_skus': unmatched_skus,
        'errors': errors
    }


def edit_shipment_detail(detail_id: int, data, shipment_header_id=None):
    detail = _get_child(ShipmentDetail, detail_id, shipment_header_id, 'shipment detail')
    for k, v in _parse_detail(data).items():
        setattr(detail, k, v)
    db.session.commit()
    return {
        "success": True,
        "message": "Shipment detail updated successfully",
        "data": _detail_json(detail)
    }, 200


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def _invoice_json(i):
    return {
        'id': i.id,
        'shipment_header_id': i.shipment_header_id,
        'vendor_name': i.vendor_name,
        'invoice_no': i.invoice_no,
        'invoice_date': i.invoice_date.isoformat() if i.invoice_date else None,
        'amount': float(i.amount) if i.amount is not None else None,
        'invoice_type': i.invoice_type,
        'comments': i.comments
    }


def get_invoices_by_shipment_header_id(shipment_header_id):
    invoices = Invoice.query.filter_by(
        shipment_header_id=shipment_header_id
    ).order_by(Invoice.invoice_date.asc()).all()
    return jsonify([_invoice_json(i) for i in invoices])


def add_new_invoice(shipment_header_id, data) -> int:
    _require_shipment(shipment_header_id)
    inv = _parse_invoice(data)
    _check_invoice_unique(shipment_header_id, inv['vendor_name'], inv['invoice_no'])
    invoice = Invoice(shipment_header_id=shipment_header_id, **inv)
    db.session.add(invoice)
    db.session.commit()
    return invoice.id


def edit_invoice(invoice_id: int, data, shipment_header_id=None):
    invoice = _get_child(Invoice, invoice_id, shipment_header_id, 'invoice')
    inv = _parse_invoice(data, current_type=invoice.invoice_type)
    _check_invoice_unique(invoice.shipment_header_id, inv['vendor_name'], inv['invoice_no'], exclude_id=invoice.id)

    paid = _paid_on_invoice(invoice.id)
    if inv['amount'] < paid and inv['amount'] < invoice.amount:
        raise ApiError(f"Invoice amount {inv['amount']} is less than the {paid} already paid against it", 409)

    for k, v in inv.items():
        setattr(invoice, k, v)
    db.session.commit()
    return {
        "success": True,
        "message": "Invoice updated successfully",
        "data": _invoice_json(invoice)
    }, 200


def delete_invoice(invoice_id: int, shipment_header_id=None):
    invoice = _get_child(Invoice, invoice_id, shipment_header_id, 'invoice')
    n = Payment.query.filter_by(invoice_id=invoice.id).count()
    if n:
        raise ApiError(
            f'Cannot delete invoice: {n} payment(s) are recorded against it. '
            f'Delete or re-link those payments first.', 409)
    db.session.delete(invoice)
    db.session.commit()
    return {"success": True, "message": "Invoice deleted successfully"}, 200


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def get_all_payments():
    payments = Payment.query.all()
    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
            'invoice_id': p.invoice_id,
            'payment_date': p.payment_date.isoformat(),
            'description': p.description,
            'amount': float(p.amount),
            'fee': float(p.fee),
        }
        for p in payments
    ])


def get_payments_by_shipment_header_id(shipment_header_id):
    payments = Payment.query.filter_by(shipment_header_id=shipment_header_id
                ).order_by(Payment.payment_date.asc()).all()

    return jsonify([
        {
            'id': p.id,
            'shipment_header_id': p.shipment_header_id,
            'invoice_id': p.invoice_id,
            'invoice_no': p.invoice.invoice_no if p.invoice else None,
            'vendor_name': p.invoice.vendor_name if p.invoice else None,
            'payment_date': p.payment_date.isoformat() if p.payment_date else None,
            'description': p.description,
            'amount': float(p.amount) if p.amount is not None else None,
            'fee': float(p.fee) if p.fee is not None else None,
            'comments': p.comments
        } for p in payments
    ])


def add_new_payment(shipment_header_id, data) -> int:
    _require_shipment(shipment_header_id)
    p = _parse_payment(data)
    _check_payment_invoice(shipment_header_id, p)
    payment = Payment(shipment_header_id=shipment_header_id, **p)
    db.session.add(payment)
    db.session.commit()
    return payment.id


def edit_payment(payment_id: int, data, shipment_header_id=None):
    payment = _get_child(Payment, payment_id, shipment_header_id, 'payment')
    p = _parse_payment(data)
    same_invoice = payment.invoice_id == p['invoice_id']
    _check_payment_invoice(payment.shipment_header_id, p, exclude_payment_id=payment.id,
                           old_amount=payment.amount if same_invoice else None)

    for k, v in p.items():
        setattr(payment, k, v)
    db.session.commit()
    return {
        "success": True,
        "message": "Payment updated successfully",
        "data": {
            "id": payment.id,
            "shipment_header_id": payment.shipment_header_id,
            "invoice_id": payment.invoice_id,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "description": payment.description,
            "amount": float(payment.amount) if payment.amount is not None else None,
            "fee": float(payment.fee) if payment.fee is not None else None,
            "comments": payment.comments
        }
    }, 200


def delete_payment(payment_id: int, shipment_header_id=None):
    payment = _get_child(Payment, payment_id, shipment_header_id, 'payment')
    db.session.delete(payment)
    db.session.commit()
    return {"success": True, "message": "Payment deleted successfully"}, 200
