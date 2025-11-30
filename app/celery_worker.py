from app import create_app
from app.celery_app import init_celery
from app.extensions import celery

# Create Flask app
app = create_app()

# Initialize Celery WITH Flask app
init_celery(app)

# Expose Celery for worker
