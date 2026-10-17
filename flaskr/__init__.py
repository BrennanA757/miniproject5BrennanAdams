# Brennan Adams
# INF601 Advanced Programming with Python
# Mini Project 5 Flask Project

import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='agoodkey',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    app.cli.add_command(db.init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import order
    app.register_blueprint(order.bp)
    app.add_url_rule('/', endpoint="index")

    return app
