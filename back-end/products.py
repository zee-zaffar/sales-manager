from flask import jsonify
from db_models import Products
from main import db
from typing import Any

def get_all_products():
    products = Products.query.all()
    return jsonify([
        {
            'code': p.code,
            'category': p.category,
            'description': p.description,
            'color': p.color,
            'cost': float(p.cost),
            'comments': p.comments
        } for p in products
    ])

def add_new_product(data: Any) -> int:
    product = Products(
        code=data.get('code'),
        category=data.get('category'),
        description=data.get('description'),
        color=data.get('color'),
        cost=float(data.get('cost')) if data.get('cost') is not None else None,
        comments=data.get('comments')
    )
    db.session.add(product)
    db.session.commit()
    return product.code