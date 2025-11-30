from flask import Flask
from .database import init_db
from .api import api_bp
from .metrics import setup_metrics
from .celery_app import create_celery_app

celery = None

def create_app():
    global celery
    
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    init_db(app)
    setup_metrics(app)
    app.register_blueprint(api_bp)

    celery = create_celery_app(app)

    return app
