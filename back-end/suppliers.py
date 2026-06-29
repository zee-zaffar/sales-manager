from flask import jsonify, request
from db_models import Supplier
from main import db


def get_all_suppliers():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return jsonify([
        {
            'id':           s.id,
            'name':         s.name,
            'contact_name': s.contact_name,
            'email':        s.email,
            'phone':        s.phone,
            'address':      s.address,
            'comments':     s.comments
        } for s in suppliers
    ])


def add_new_supplier():
    data = request.json
    supplier = Supplier(
        name=data.get('name'),
        contact_name=data.get('contact_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        comments=data.get('comments')
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'id': supplier.id}), 201


def update_supplier(supplier_id: int):
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.json
    supplier.name         = data.get('name',         supplier.name)
    supplier.contact_name = data.get('contact_name', supplier.contact_name)
    supplier.email        = data.get('email',        supplier.email)
    supplier.phone        = data.get('phone',        supplier.phone)
    supplier.address      = data.get('address',      supplier.address)
    supplier.comments     = data.get('comments',     supplier.comments)
    db.session.commit()
    return jsonify({'id': supplier.id}), 200
