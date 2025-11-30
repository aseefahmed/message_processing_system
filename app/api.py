from flask import Blueprint, request, jsonify
from .models import Message
from .database import db
from .tasks import process_message
from prometheus_client import Counter


api_bp = Blueprint("api", __name__)


requests_total = Counter("api_requests_total", "Total API Requests", ["endpoint", "method"])
errors_total = Counter("api_errors_total", "API Errors", ["endpoint"])
messages_processed = Counter("messages_processed", "Messages processed", ["status"])


@api_bp.before_request
def before():
    requests_total.labels(endpoint=request.path, method=request.method).inc()


@api_bp.route("/messages", methods=["POST"])
def create_message():
    data = request.json
    msg = Message(content=data.get("content"))
    db.session.add(msg)
    db.session.commit()


    process_message.delay(msg.id)
    return jsonify({"id": msg.id, "status": msg.status})


@api_bp.route("/messages", methods=["GET"])
def list_messages():
    status_filter = request.args.get("status")
    query = Message.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    return jsonify([{
    "id": m.id,
    "content": m.content,
    "status": m.status
    } for m in query.all()])


@api_bp.route("/messages/<id>")
def get_message(id):
    msg = Message.query.get_or_404(id)
    return jsonify({"id": msg.id, "content": msg.content, "status": msg.status})


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
        "failed": failed
    })