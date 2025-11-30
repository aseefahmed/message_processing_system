from prometheus_client import generate_latest
from flask import Response


def setup_metrics(app):
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")