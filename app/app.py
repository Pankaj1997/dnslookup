from flask import Flask
from routes import routes  # Import the routes Blueprint
import signal
import sys

def cleanup():
    print("Performing cleanup...")

def graceful_shutdown(signum, frame):
    print("Signal received, shutting down gracefully...")
    cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, graceful_shutdown)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, graceful_shutdown) # Handle `docker stop`


app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
