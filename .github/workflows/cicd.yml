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
