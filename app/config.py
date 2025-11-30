class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///messages.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND = "redis://redis:6379/1"