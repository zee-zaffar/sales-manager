from flask import request, jsonify
from db_models import Orders
from main import db

# Get all orders
def get_orders():
    orders = Orders.query.all()
    return jsonify([
        {
            'order_no': o.order_no,
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'qty': o.qty,
            'source': o.source,
            'color': o.color,
            'source': o.source,
            'platform': o.platform,
            'order_amount': float(o.order_amount) if o.order_amount else None,
            'sales_tax': float(o.sales_tax) if o.sales_tax else None,
            'comments': o.comments
        } for o in orders
    ])

# Insert a new order
def insert_order():
    data = request.json
    order = Orders(
        order_no=data.get('order_no'),
        order_date=data.get('order_date'),
        qty=data.get('qty'),
        color=data.get('color'),
        source=data.get('source'),
        platform=data.get('platform'),
        order_amount=data.get('order_amount'),
        sales_tax=data.get('sales_tax'),
        comments=data.get('comments')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'order_no': order.order_no}), 201

# Query an order by order_no
def get_order_by_no(order_no):
    order = Orders.query.filter_by(order_no=order_no).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify({
        'order_no': order.order_no,
        'order_date': order.order_date.isoformat() if order.order_date else None,
        'qty': order.qty,
        'color': order.color,
        'source': order.source,
        'platform': order.platform,
        'order_amount': float(order.order_amount) if order.order_amount else None,
        'sales_tax': float(order.sales_tax) if order.sales_tax else None,
        'comments': order.comments
    })

# Update an order via PUT
def update_order(order_no):
    order = Orders.query.filter_by(order_no=order_no).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    data = request.json
    order.order_date = data.get('order_date', order.order_date)
    order.qty = data.get('qty', order.qty)
    order.color = data.get('color', order.color)
    order.source = data.get('source', order.source)
    order.platform = data.get('platform', order.platform)
    order.order_amount = data.get('order_amount', order.order_amount)
    order.sales_tax = data.get('sales_tax', order.sales_tax)
    order.comments = data.get('comments', order.comments)
    db.session.commit()
    return jsonify({'order_no': order.order_no, 'message': 'Order updated successfully'})




