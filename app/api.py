from flask import Blueprint, request, jsonify
from .models import Message
from .database import db
from .tasks import process_message

# Import shared Prometheus metrics (DO NOT REDECLARE)
from app.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    API_ERRORS
)

api_bp = Blueprint("api", __name__)


@api_bp.before_request
def before_request():
    request._timer = REQUEST_LATENCY.labels(request.path).time()


@api_bp.after_request
def after_request(response):
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    request._timer()
    return response


@api_bp.route("/messages", methods=["POST"])
def create_message():
    try:
        data = request.json or {}

        msg = Message(content=data.get("content"))
        db.session.add(msg)
        db.session.commit()

        process_message.delay(msg.id)

        return jsonify({"id": msg.id, "status": msg.status}), 201

    except Exception as e:
        API_ERRORS.labels(
            endpoint="/messages",
            error_type=type(e).__name__
        ).inc()

        db.session.rollback()

        return jsonify({"error": str(e)}), 500


@api_bp.route("/messages", methods=["GET"])
def list_messages():
    status_filter = request.args.get("status")
    query = Message.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    return jsonify([
        {
            "id": m.id,
            "content": m.content,
            "status": m.status,
        }
        for m in query.all()
    ])


@api_bp.route("/messages/<id>")
def get_message(id):
    msg = Message.query.get_or_404(id)
    return jsonify({
        "id": msg.id,
        "content": msg.content,
        "status": msg.status,
    })


@api_bp.route("/messages/stats")
def stats():
    total = Message.query.count()
    pending = Message.query.filter_by(status="pending").count()
    processing = Message.query.filter_by(status="processing").count()
    completed = Message.query.filter_by(status="completed").count()
    failed = Message.query.filter_by(status="failed").count()

    return jsonify({
        "total": total,
        "pending": pending,
        "processing": processing,
        "completed": completed,
        "failed": failed,
    })
