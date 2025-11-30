# app/__init__.py
from flask import Flask
from .database import init_db
from .api import api_bp
from .metrics import setup_metrics
from .celery_app import init_celery

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Init Flask services
    init_db(app)
    setup_metrics(app)
    app.register_blueprint(api_bp)

    # Init Celery
    init_celery(app)

    return app
