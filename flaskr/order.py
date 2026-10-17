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
        'SELECT o.customerID, u.username'
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
        cost = int(item1) + int(item2) + int(item3)
        error = None

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO "order" (customerId, cost)'
                ' VALUES (?, ?)',
                (g.user['customerID'], cost)
            )
            db.commit()
            return redirect(url_for('orders.index'))

    return render_template('orders/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

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
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
