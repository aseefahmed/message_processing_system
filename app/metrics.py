from flask import request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Request counters & latency histogram
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

# API errors
API_ERRORS = Counter(
    "api_errors_total",
    "Total API errors",
    ["endpoint", "error_type"]
)

# Messages processed by status
MESSAGE_STATUS = Counter(
    "messages_processed_total",
    "Messages processed by status",
    ["status"]
)

def setup_metrics(app):
    @app.before_request
    def before_request():
        request._start_time = REQUEST_LATENCY.labels(
            request.path
        ).time()

    @app.after_request
    def after_request(response):
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()

        # Observe latency
        request._start_time()  # stops the timer and records duration

        return response

    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
