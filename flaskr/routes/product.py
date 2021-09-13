from itertools import product
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from flaskr.db import get_db

bp = Blueprint('product', __name__, url_prefix='/product')

@bp.route('/')
def index():
    db = get_db()
    products_list = db.execute(
        'SELECT p.id, name, description, created, user_id, username'
        ' FROM product p JOIN user u ON u.id = p.user_id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('product/index.html', products_list=products_list)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        error = None

        if not name:
            error = 'Name is required.'
        if not description:
            error = 'Description is required.'
        if not price:
            'Price is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO product (name, description, price, quantity, user_id)'
                'VALUES (?, ?, ?, ?, ?)', 
                (name, description, price, quantity, g.user['id'])
            )
            db.commit()
            return redirect(url_for('product.index'))
    return render_template('product/create.html')

def get_product(id, check_author=True):
    product = get_db().execute(
        'SELECT p.id, name, description, created, user_id, username, price, quantity'
        ' FROM product p JOIN user u ON u.id = p.user_id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, f"Product id {id} doesn't exist")
    
    if check_author and product['user_id'] != g.user['id']:
        abort(403)

    return product

@bp.route('/<int:id>')
def single_product(id):
    product = get_product(id, check_author=False)
    return render_template('/product/product.html', product=product)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    product = get_product(id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE product SET name = ?, description = ?, price = ?, quantity = ?'
                ' WHERE id = ?',
                (name, description, price, quantity, id)
            )
            db.commit()
            return redirect(url_for('product.index'))
    return render_template('product/update.html', product=product)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_product(id)
    db = get_db()
    db.execute(
        'DELETE FROM product WHERE product.id = ?',
        (id,)
    )
    db.commit()
    return redirect(url_for('product.index'))

@bp.route('/<int:id>/add-to-cart', methods=['POST'])
def add_to_cart(id, quantity):
    print('hi')
    #xproduct = get_product(id, check_author=False)
    #if request.method == 'POST':
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append({'id': id, 'quantity': quantity})
    session.modified = True
    return redirect(url_for('product.index'))
    #return render_template('product/product.html', product=product)

