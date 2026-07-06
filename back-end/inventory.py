from flask import jsonify
from sqlalchemy import func
from db_models import Products, ShipmentDetail, Orders
from main import db

def get_inventory():
    """
    Driven by shipment_detail SKUs (what has actually been received), not the
    products catalog, since a SKU can be received before it's ever added as a
    formal product record. The products table only supplies extra metadata
    (category/color) when a matching entry exists. Cost is an average landed
    cost, manually entered per shipment line (falling back to unit_price when
    not entered), averaged across every shipment that SKU was received in.
    """
    details = ShipmentDetail.query.all()

    agg = {}
    for d in details:
        a = agg.setdefault(d.sku, {'received': 0, 'landed_total': 0.0, 'description': None})
        qty = d.quantity or 0
        unit_landed_cost = float(d.landed_cost) if d.landed_cost is not None else float(d.unit_price or 0)
        a['received'] += qty
        a['landed_total'] += unit_landed_cost * qty
        if not a['description'] and d.description:
            a['description'] = d.description

    ordered_by_sku = dict(
        db.session.query(Orders.sku, func.sum(Orders.qty))
        .group_by(Orders.sku)
        .all()
    )

    products_by_code = {p.code: p for p in Products.query.all()}

    result = []
    for sku in sorted(agg.keys(), key=lambda s: s or ''):
        a = agg[sku]
        product = products_by_code.get(sku)
        received = int(a['received'] or 0)
        ordered = int(ordered_by_sku.get(sku) or 0)
        avg_landed_cost = (a['landed_total'] / received) if received else None
        result.append({
            'code': sku,
            'category': product.category if product else None,
            'description': product.description if product else a['description'],
            'color': product.color if product else None,
            'avg_landed_cost': round(avg_landed_cost, 2) if avg_landed_cost is not None else None,
            'received': received,
            'ordered': ordered,
            'on_hand': received - ordered,
        })
    return jsonify(result)
