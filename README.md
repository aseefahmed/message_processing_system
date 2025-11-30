# N3Hub

A Flask-based message processing application with asynchronous task processing using Celery and Redis. The application provides a RESTful API for managing messages, tracks their processing status, and includes comprehensive Prometheus metrics for monitoring.

## What is this?

N3Hub is a microservice application that demonstrates a production-ready architecture for handling asynchronous message processing. It consists of:

- **Flask Web API**: RESTful API endpoints for creating, retrieving, and monitoring messages
- **Celery Workers**: Background workers that process messages asynchronously
- **Redis**: Message broker and result backend for Celery tasks
- **SQLite Database**: Persistent storage for messages and their status
- **Prometheus Metrics**: Built-in metrics endpoint for monitoring application health and performance

### Key Features

- **Message Management**: Create, list, and retrieve messages via REST API
- **Asynchronous Processing**: Messages are processed in the background using Celery workers
- **Status Tracking**: Messages have statuses: `pending`, `processing`, `completed`, or `failed`
- **Statistics Endpoint**: Get real-time statistics about message processing
- **Metrics Endpoint**: Prometheus-compatible metrics at `/metrics`
- **Error Handling**: Comprehensive error tracking and retry mechanisms

### API Endpoints

- `POST /messages` - Create a new message
- `GET /messages` - List all messages (optional `?status=<status>` filter)
- `GET /messages/<id>` - Get a specific message by ID
- `GET /messages/stats` - Get message statistics (total, pending, processing, completed, failed)
- `GET /metrics` - Prometheus metrics endpoint

## Quick Start (docker-compose up)

The easiest way to get started with N3Hub is using Docker Compose, which will set up all required services:

### Prerequisites

- Docker and Docker Compose installed on your system
- At least 2GB of available RAM

### Steps

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd n3hub_project
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Flask application Docker image
   - Start the web service (Flask API) on port 5000
   - Start the Celery worker service
   - Start Redis on port 6379

3. **Verify the services are running**:
   ```bash
   docker-compose ps
   ```

   You should see three services running: `web`, `worker`, and `redis`.

4. **Test the API**:
   ```bash
   # Create a message
   curl -X POST http://localhost:5000/messages \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello, N3Hub!"}'

   # Get all messages
   curl http://localhost:5000/messages

   # Get message statistics
   curl http://localhost:5000/messages/stats

   # Get Prometheus metrics
   curl http://localhost:5000/metrics
   ```

5. **View logs**:
   ```bash
   # View all logs
   docker-compose logs -f

   # View logs for a specific service
   docker-compose logs -f web
   docker-compose logs -f worker
   ```

6. **Stop the services**:
   ```bash
   docker-compose down
   ```

### Docker Compose Services

- **web**: Flask application served with Gunicorn (port 5000)
- **worker**: Celery worker for processing messages asynchronously
- **redis**: Redis server for Celery broker and result backend (port 6379)

## How to Test Locally

### Option 1: Using Docker Compose (Recommended)

Follow the Quick Start guide above. This is the recommended approach as it matches the production environment.

### Option 2: Local Development Setup

For local development without Docker:

1. **Prerequisites**:
   - Python 3.11 or higher
   - Redis server running locally
   - Virtual environment (recommended)

2. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start Redis**:
   ```bash
   # On Linux/Mac
   redis-server

   # On Windows (if installed)
   redis-server

   # Or using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Update configuration** (if needed):
   Edit `app/config.py` to use `localhost` instead of `redis`:
   ```python
   CELERY_BROKER_URL = "redis://localhost:6379/0"
   CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
   ```

5. **Initialize the database**:
   ```bash
   python -c "from app import create_app; app = create_app(); app.app_context().push()"
   ```

6. **Start the Flask application** (in one terminal):
   ```bash
   python run.py
   ```

7. **Start the Celery worker** (in another terminal):
   ```bash
   celery -A app.celery_worker.celery worker --loglevel=info
   ```

8. **Run tests**:
   ```bash
   pytest -v
   ```

   Or with coverage:
   ```bash
   pytest --cov=app --cov-report=html
   ```

### Testing the API

Once the services are running, you can test the API:

```bash
# Create a message
curl -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'

# Expected response:
# {"id": 1, "status": "pending"}

# List all messages
curl http://localhost:5000/messages

# Get message statistics
curl http://localhost:5000/messages/stats

# Get a specific message
curl http://localhost:5000/messages/1

# Check metrics
curl http://localhost:5000/metrics
```

### Running Tests

The project includes pytest for testing:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py
```

### Project Structure

```
n3hub_project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── api.py               # API routes and endpoints
│   ├── celery_app.py        # Celery configuration
│   ├── celery_worker.py     # Celery worker entry point
│   ├── config.py            # Application configuration
│   ├── database.py          # Database initialization
│   ├── extensions.py        # Flask extensions
│   ├── metrics.py           # Prometheus metrics setup
│   ├── models.py            # SQLAlchemy models
│   └── tasks.py             # Celery tasks
├── tests/
│   └── test_api.py          # API tests
├── docker/
│   ├── prometheus.yaml      # Prometheus configuration
│   └── alerts.yaml          # Alert rules
├── grafana/
│   └── dashboard.json       # Grafana dashboard
├── docker-compose.yaml      # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

### Environment Variables

- `FLASK_ENV`: Set to `production` for production mode (defaults to development)

### Database

The application uses SQLite by default, with the database file stored in the `instance/` directory as `messages.db`. In production, you may want to configure a PostgreSQL or MySQL database.

### Monitoring

The application exposes Prometheus metrics at `/metrics`. Key metrics include:

- `http_requests_total`: Total HTTP requests by method, endpoint, and status
- `http_request_latency_seconds`: HTTP request latency histogram
- `api_errors_total`: Total API errors by endpoint and error type
- `messages_processed_total`: Messages processed by status

For more information on deployment and monitoring, see [DEPLOYMENT.md](DEPLOYMENT.md).

