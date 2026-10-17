from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('orders', __name__)


@bp.route('/')
def index():
    db = get_db()
    _orders = db.execute(
        'SELECT o.customerID, u.username, o.createdAt, o.id, o.cost, o.item1Quantity, o.item2Quantity, o.item3Quantity'
        ' FROM "order" o JOIN user u ON o.customerID = u.customerID'
    ).fetchall()
    return render_template('orders/index.html', _orders=_orders)


@bp.route('/orders', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        item1 = request.form['item1']
        item2 = request.form['item2']
        item3 = request.form['item3']
        cost = request.form['total']
        error = None

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO "order" (customerId, cost, item1Quantity, item2Quantity, item3Quantity)'
                ' VALUES (?, ?, ?, ?, ?)',
                (g.user['customerID'], cost, int(item1), int(item2), int(item3))
            )
            db.commit()
            return redirect(url_for('orders.index'))

    return render_template('orders/create.html')


def get_order(id, check_author=True):
    order = get_db().execute(
        'SELECT o.id, o.customerID, o.cost, o.createdAt'
        ' FROM order o JOIN user u ON o.customerID = u.customerID'
        ' WHERE o.customerID = ?',
        (id,)
    ).fetchone()

    if order is None:
        abort(404, f"Order id {id} doesn't exist.")

    if check_author and order['customerID'] != g.user['id']:
        abort(403)

    return order


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    order = get_order(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE "order" SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('orders/update.html', order=order)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_order(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
