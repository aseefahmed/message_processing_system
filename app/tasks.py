import time
from app.models import Message
from app.database import db
from app.metrics import MESSAGE_STATUS

from celery import shared_task


@shared_task(bind=True)
def process_message(self, message_id):
    msg = Message.query.get(message_id)

    try:
        msg.status = "processing"
        db.session.commit()

        time.sleep(3)

        msg.status = "completed"
        db.session.commit()
        MESSAGE_STATUS.labels("completed").inc()

    except Exception as e:
        msg.status = "failed"
        db.session.commit()
        MESSAGE_STATUS.labels("failed").inc()
        raise self.retry(exc=e)
