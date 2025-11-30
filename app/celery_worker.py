# app/celery_worker.py

from app import create_app, celery

# Initialize Flask app first. This will also initialize Celery.
app = create_app()

# Nothing else needed — Celery is already set up inside create_app()
