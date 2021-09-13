from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import MethodNotAllowed, abort
from .auth import login_required
from flaskr.db import get_db

bp = Blueprint('purchase', __name__)

@bp.route('/list-purchases', methods=['GET'])
def list_purchases():
    user_id = g.user['id']
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?',
        (user_id,)
    ).fetchone()
    purchases = db.execute(
        'SELECT p.name, p.price, pur.date FROM product p'
        ' JOIN purchase AS pur ON pur.product_id = p.id'
        ' WHERE pur.user_id = ?',
        (g.user['id'],)
    ).fetchall()
    return render_template('purchase/list-purchases.html', purchases=purchases, user=user)

@bp.route('/checkout', methods=['POST', 'GET'])
def checkout():
    user_id = g.user['id']
    error = None

    if request.method == 'POST':
        cart = session['cart']
        for product in cart:
            product_id = product['id']
            payment_selected = request.form['payment']
            address_selected = request.form['address']
            db = get_db()
            db.execute(
                'INSERT INTO purchase (user_id, product_id, address, payment)'
                ' VALUES (?, ?, ?, ?)',
                (user_id, product_id, address_selected, payment_selected)
            )
            db.commit()
        session['cart'] = []
        return redirect(url_for('purchase.list_purchases'))
    return render_template('purchase/purchase.html')

@bp.route('/cart', methods=['POST', 'GET'])
@login_required
def cart():
    items = session['cart']
    if request.method == 'POST':
        return redirect(url_for('product.index'))
    return render_template('purchase/cart.html', items=items)

