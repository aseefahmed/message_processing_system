# app/tasks.py
import time
from app.extensions import celery
from app.models import Message
from app.database import db

@celery.task(bind=True)
def process_message(self, message_id):
    msg = Message.query.get(message_id)

    try:
        msg.status = "processing"
        db.session.commit()

        time.sleep(3)

        msg.status = "completed"
        db.session.commit()

    except Exception as e:
        msg.status = "failed"
        db.session.commit()
        raise self.retry(exc=e)
