from flask import request, jsonify
from sqlalchemy import func
from db_models import Orders
from main import db

def _serialize(o):
    cogs     = float(o.cost_of_goods  or 0)
    ship     = float(o.shipping_cost  or 0)
    fee      = float(o.platform_fee   or 0)
    revenue  = float(o.order_amount   or 0)
    tax      = float(o.sales_tax      or 0)
    return {
        'order_no':      o.order_no,
        'order_date':    o.order_date.isoformat() if o.order_date else None,
        'qty':           o.qty,
        'sku':           o.sku,
        'source':        o.source,
        'color':         o.color,
        'platform':      o.platform,
        'order_amount':  revenue,
        'sales_tax':     tax,
        'cost_of_goods': cogs,
        'shipping_cost': ship,
        'platform_fee':  fee,
        'net_profit':    round(revenue - tax - cogs - ship - fee, 2),
        'comments':      o.comments,
    }

def get_orders():
    orders = Orders.query.order_by(Orders.order_date.desc()).all()
    return jsonify([_serialize(o) for o in orders])

def insert_order():
    data = request.json
    order = Orders(
        order_no=data.get('order_no'),
        order_date=data.get('order_date'),
        qty=data.get('qty'),
        sku=data.get('sku') or None,
        color=data.get('color'),
        source=data.get('source'),
        platform=data.get('platform'),
        order_amount=data.get('order_amount'),
        sales_tax=data.get('sales_tax'),
        cost_of_goods=data.get('cost_of_goods', 0),
        shipping_cost=data.get('shipping_cost', 0),
        platform_fee=data.get('platform_fee', 0),
        comments=data.get('comments'),
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'order_no': order.order_no}), 201

def get_order_by_no(order_no):
    order = Orders.query.filter_by(order_no=order_no).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(_serialize(order))

def update_order(order_no):
    order = Orders.query.filter_by(order_no=order_no).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    data = request.json
    order.order_date    = data.get('order_date',    order.order_date)
    order.qty           = data.get('qty',           order.qty)
    order.sku           = data.get('sku',           order.sku) or None
    order.color         = data.get('color',         order.color)
    order.source        = data.get('source',        order.source)
    order.platform      = data.get('platform',      order.platform)
    order.order_amount  = data.get('order_amount',  order.order_amount)
    order.sales_tax     = data.get('sales_tax',     order.sales_tax)
    order.cost_of_goods = data.get('cost_of_goods', order.cost_of_goods)
    order.shipping_cost = data.get('shipping_cost', order.shipping_cost)
    order.platform_fee  = data.get('platform_fee',  order.platform_fee)
    order.comments      = data.get('comments',      order.comments)
    db.session.commit()
    return jsonify({'order_no': order.order_no, 'message': 'Updated'})

def get_monthly_summary():
    month_label = func.to_char(Orders.order_date, 'YYYY-MM')
    rows = (
        db.session.query(
            month_label.label('month'),
            func.count(Orders.order_no).label('order_count'),
            func.sum(Orders.order_amount).label('revenue'),
            func.sum(Orders.sales_tax).label('tax'),
            func.sum(Orders.cost_of_goods).label('cogs'),
            func.sum(Orders.shipping_cost).label('shipping'),
            func.sum(Orders.platform_fee).label('fees'),
        )
        .group_by(month_label)
        .order_by(month_label.desc())
        .all()
    )
    result = []
    for r in rows:
        revenue  = float(r.revenue  or 0)
        tax      = float(r.tax      or 0)
        cogs     = float(r.cogs     or 0)
        shipping = float(r.shipping or 0)
        fees     = float(r.fees     or 0)
        result.append({
            'month':       r.month,
            'order_count': r.order_count,
            'revenue':     revenue,
            'tax':         tax,
            'cogs':        cogs,
            'shipping':    shipping,
            'fees':        fees,
            'net_profit':  round(revenue - tax - cogs - shipping - fees, 2),
        })
    return jsonify(result)
