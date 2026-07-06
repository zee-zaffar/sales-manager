from flask import jsonify
from db_models import Products, ShipmentDetail
from main import db
from typing import Any

def get_all_products(active_only: bool = False):
    query = Products.query
    if active_only:
        query = query.filter_by(active=True)
    products = query.order_by(Products.code).all()
    return jsonify([
        {
            'code': p.code,
            'category': p.category,
            'description': p.description,
            'color': p.color,
            'active': p.active,
            'comments': p.comments
        } for p in products
    ])

def add_new_product(data: Any) -> int:
    product = Products(
        code=data.get('code'),
        category=data.get('category'),
        description=data.get('description'),
        color=data.get('color'),
        active=data.get('active', True),
        comments=data.get('comments')
    )
    db.session.add(product)
    db.session.commit()
    return product.code

def update_product_active(code: str, active: bool):
    product = Products.query.get(code)
    if not product:
        return {
            "error": "Product not found",
            "message": f"No product found with code {code}"
        }, 404

    product.active = bool(active)
    db.session.commit()

    return {
        "success": True,
        "code": product.code,
        "active": product.active
    }, 200

def update_product(code: str, data: Any):
    product = Products.query.get(code)
    if not product:
        return {
            "error": "Product not found",
            "message": f"No product found with code {code}"
        }, 404

    new_code = (data.get('code') or code).strip()
    if new_code != code and Products.query.get(new_code):
        return {
            "error": "Code already in use",
            "message": f"A product with code {new_code} already exists"
        }, 400

    try:
        product.category = data.get('category')
        product.description = data.get('description')
        product.color = data.get('color')
        product.comments = data.get('comments')

        if new_code != code:
            # shipment_detail.sku has no FK (it can reference SKUs that predate
            # the catalog), so it isn't kept in sync automatically — update it
            # here. orders.sku has ON UPDATE CASCADE and follows automatically.
            ShipmentDetail.query.filter_by(sku=code).update({'sku': new_code})
            product.code = new_code

        db.session.commit()

        return {
            "success": True,
            "message": "Product updated successfully",
            "data": {
                "code": product.code,
                "category": product.category,
                "description": product.description,
                "color": product.color,
                "active": product.active,
                "comments": product.comments
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {
            "error": "Internal server error",
            "message": f"Failed to update product: {str(e)}"
        }, 500

def delete_product(code: str):
    product = Products.query.get(code)
    if not product:
        return {
            "error": "Product not found",
            "message": f"No product found with code {code}"
        }, 404

    db.session.delete(product)
    db.session.commit()

    return {"success": True, "message": "Product deleted successfully"}, 200
