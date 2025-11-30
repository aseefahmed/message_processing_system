from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    from . import models
    with app.app_context():
        db.create_all()