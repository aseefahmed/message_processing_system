from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Running with Flask’s built-in server (Dev only)
    # In production, use Gunicorn via Docker
    app.run(host="0.0.0.0", port=5000)