# Deployment Guide

This guide covers deploying N3Hub to production using GitHub Actions and monitoring the application.

## Prerequisites

Before deploying N3Hub to production, ensure you have:

1. **GitHub Repository**: A GitHub repository with the N3Hub codebase
2. **Docker Hub Account**: An account on Docker Hub (or another container registry)
3. **Production Server**: A server or cloud platform (AWS, GCP, Azure, DigitalOcean, etc.) with:
   - Docker and Docker Compose installed
   - At least 2GB RAM
   - Network access to pull Docker images
4. **GitHub Secrets**: Access to configure secrets in your GitHub repository
5. **Domain Name** (optional): For production access
6. **SSL Certificate** (optional): For HTTPS (can use Let's Encrypt)

### Required GitHub Secrets

Configure the following secrets in your GitHub repository settings (`Settings` → `Secrets and variables` → `Actions`):

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not password)

To create a Docker Hub token:
1. Log in to Docker Hub
2. Go to Account Settings → Security → New Access Token
3. Create a token with read/write permissions
4. Copy the token and add it as `DOCKERHUB_TOKEN` secret

## How to Deploy to Production (Using GitHub Actions)

N3Hub uses GitHub Actions for CI/CD. The workflow automatically builds, tests, and pushes Docker images when code is pushed to the `main` branch.

### CI/CD Pipeline Overview

The GitHub Actions workflow (`.github/workflows/cicd.yml`) performs the following steps:

1. **Checkout Code**: Retrieves the latest code from the repository
2. **Setup Python**: Configures Python 3.11 environment
3. **Install Dependencies**: Installs project dependencies and pytest
4. **Run Tests**: Executes the test suite
5. **Docker Build**: Builds the Docker image
6. **Docker Push**: Pushes the image to Docker Hub

### Setting Up the CI/CD Pipeline

1. **Ensure the workflow file exists**:
   The workflow file should be located at `.github/workflows/cicd.yml`. If it doesn't exist, create it with the following content:

   ```yaml
   name: CI/CD Pipeline

   on:
     push:
       branches: [ "main" ]

   jobs:
     build-test-push:
       runs-on: ubuntu-latest

       steps:
       # Checkout code
       - name: Checkout Code
         uses: actions/checkout@v3

       # Set up Python for tests
       - name: Setup Python
         uses: actions/setup-python@v4
         with:
           python-version: "3.11"

       # Install dependencies
       - name: Install Dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
           pip install pytest

       # Run tests
       - name: Run Tests
         run: pytest -v

       # Login to Docker Hub
       - name: Log in to Docker Hub
         uses: docker/login-action@v3
         with:
           username: ${{ secrets.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}

       # Build Docker image
       - name: Build Docker Image
         run: |
           docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/n3hub:latest .

       # Push Docker Image
       - name: Push Docker Image
         run: |
           docker push ${{ secrets.DOCKERHUB_USERNAME }}/n3hub:latest
   ```

2. **Configure GitHub Secrets**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`

3. **Push to main branch**:
   ```bash
   git push origin main
   ```

4. **Monitor the workflow**:
   - Go to the "Actions" tab in your GitHub repository
   - Watch the workflow run and verify it completes successfully

### Deploying to Production Server

Once the Docker image is built and pushed, deploy it to your production server:

1. **SSH into your production server**:
   ```bash
   ssh user@your-production-server
   ```

2. **Clone or update the repository**:
   ```bash
   git clone <repository-url>
   cd n3hub_project
   # Or if already cloned:
   git pull origin main
   ```

3. **Update docker-compose.yaml for production** (if needed):
   You may want to:
   - Remove port mappings for Redis (security)
   - Add environment variables
   - Configure volume mounts for persistent storage
   - Add restart policies

   Example production `docker-compose.yaml`:
   ```yaml
   version: "3.9"

   services:
     web:
       image: <your-dockerhub-username>/n3hub:latest
       ports:
         - "5000:5000"
       depends_on:
         - redis
       environment:
         - FLASK_ENV=production
       restart: unless-stopped
       volumes:
         - ./instance:/app/instance

     worker:
       image: <your-dockerhub-username>/n3hub:latest
       command: celery -A app.celery_worker.celery worker --loglevel=info
       depends_on:
         - redis
         - web
       restart: unless-stopped
       volumes:
         - ./instance:/app/instance

     redis:
       image: redis:7-alpine
       restart: unless-stopped
       volumes:
         - redis-data:/data

   volumes:
     redis-data:
   ```

4. **Pull the latest image and start services**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Verify deployment**:
   ```bash
   # Check service status
   docker-compose ps

   # Check logs
   docker-compose logs -f

   # Test the API
   curl http://localhost:5000/messages/stats
   ```

6. **Set up a reverse proxy** (recommended):
   Use Nginx or Traefik to:
   - Handle SSL/TLS termination
   - Route traffic to the application
   - Provide better security

   Example Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Automated Deployment Script

You can create a deployment script to automate the process:

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Pulling latest code..."
git pull origin main

echo "Pulling latest Docker images..."
docker-compose pull

echo "Stopping services..."
docker-compose down

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Checking service health..."
docker-compose ps

echo "Deployment complete!"
```

Make it executable and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

## How to Monitor

N3Hub includes built-in Prometheus metrics for monitoring. Here's how to set up comprehensive monitoring:

### 1. Prometheus Setup

Prometheus can scrape metrics from the application's `/metrics` endpoint.

**Using Docker Compose** (add to your `docker-compose.yaml`):

```yaml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus.yaml:/etc/prometheus/prometheus.yml
      - ./docker/alerts.yaml:/etc/prometheus/alerts.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
```

**Prometheus Configuration** (`docker/prometheus.yaml`):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flask_app'
    static_configs:
      - targets: ['web:5000']
```

### 2. Grafana Dashboard

Import the Grafana dashboard (`grafana/dashboard.json`) to visualize metrics:

1. Access Grafana (typically at `http://localhost:3000`)
2. Go to Dashboards → Import
3. Upload `grafana/dashboard.json`
4. Configure the Prometheus data source if not already set

**Key Metrics to Monitor**:

- **Request Rate**: `rate(http_requests_total[5m])`
- **Error Rate**: `rate(api_errors_total[5m])`
- **Request Latency**: `histogram_quantile(0.95, http_request_latency_seconds_bucket)`
- **Message Processing**: `messages_processed_total`
- **Queue Depth**: Count of pending messages

### 3. Alerting

Configure alerts in Prometheus using `docker/alerts.yaml`:

```yaml
groups:
  - name: n3hub_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_latency_seconds_bucket) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "95th percentile latency is above 1 second"

      - alert: WorkerDown
        expr: up{job="flask_app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Application is down"
          description: "The Flask application is not responding"
```

### 4. Health Checks

Monitor application health:

```bash
# Check if the API is responding
curl http://localhost:5000/messages/stats

# Check metrics endpoint
curl http://localhost:5000/metrics

# Check Docker container health
docker-compose ps
```

### 5. Log Monitoring

Monitor application logs:

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f worker

# View logs with timestamps
docker-compose logs -f --timestamps
```

For production, consider integrating with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (Grafana's log aggregation system)
- **Cloud logging** (AWS CloudWatch, GCP Cloud Logging, Azure Monitor)

## Basic Troubleshooting

### Issue 1: Services Won't Start

**Symptoms**: `docker-compose up` fails or containers exit immediately

**Solutions**:

1. **Check logs**:
   ```bash
   docker-compose logs
   ```

2. **Verify Redis is running**:
   ```bash
   docker-compose ps redis
   # Should show "Up"
   ```

3. **Check port conflicts**:
   ```bash
   # Check if port 5000 is already in use
   netstat -tulpn | grep 5000
   # Or on Mac:
   lsof -i :5000
   ```
   If port 5000 is in use, change it in `docker-compose.yaml`:
   ```yaml
   ports:
     - "8080:5000"  # Use port 8080 instead
   ```

4. **Rebuild images**:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

5. **Check Docker resources**:
   ```bash
   docker system df
   docker system prune  # Clean up if needed
   ```

### Issue 2: Messages Not Processing

**Symptoms**: Messages remain in "pending" status and never get processed

**Solutions**:

1. **Check Celery worker status**:
   ```bash
   docker-compose logs worker
   ```
   Look for errors or connection issues.

2. **Verify Redis connection**:
   ```bash
   # Test Redis connectivity from worker container
   docker-compose exec worker python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
   ```
   Should output `True`.

3. **Check worker is running**:
   ```bash
   docker-compose ps worker
   ```
   Should show "Up" status.

4. **Restart worker**:
   ```bash
   docker-compose restart worker
   ```

5. **Check database connectivity**:
   ```bash
   docker-compose exec web python -c "from app import create_app; app = create_app(); print('DB OK')"
   ```

### Issue 3: High Memory Usage or Performance Issues

**Symptoms**: Application is slow, containers are using too much memory

**Solutions**:

1. **Monitor resource usage**:
   ```bash
   docker stats
   ```

2. **Check for memory leaks**:
   - Review application logs for errors
   - Check Prometheus metrics for increasing memory usage
   - Monitor message queue depth

3. **Scale workers** (if needed):
   ```yaml
   # In docker-compose.yaml, add more worker instances
   worker:
     # ... existing config
   worker2:
     image: <your-image>
     command: celery -A app.celery_worker.celery worker --loglevel=info
     # ... same config as worker
   ```

4. **Optimize Redis**:
   - Check Redis memory usage: `docker-compose exec redis redis-cli INFO memory`
   - Set max memory if needed: `redis-cli CONFIG SET maxmemory 256mb`

5. **Database optimization**:
   - If using SQLite, consider migrating to PostgreSQL for production
   - Add database indexes if querying large datasets
   - Regularly clean up old messages if not needed

### Additional Troubleshooting Commands

```bash
# View all running containers
docker-compose ps

# View resource usage
docker stats

# Execute commands in containers
docker-compose exec web bash
docker-compose exec worker bash

# Check Redis status
docker-compose exec redis redis-cli ping

# View network configuration
docker network ls
docker network inspect n3hub_project_default

# Clean up stopped containers
docker-compose down
docker system prune -a  # Remove unused images
```

### Getting Help

If issues persist:

1. Check the logs thoroughly: `docker-compose logs -f`
2. Review Prometheus metrics: `curl http://localhost:5000/metrics`
3. Verify all environment variables are set correctly
4. Ensure all prerequisites are met
5. Check GitHub Actions workflow for build/test failures
