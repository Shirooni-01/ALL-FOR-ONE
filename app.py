import os
import sys
import logging
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from config import get_config
from routes.auth import init_auth
from routes.notes import init_notes
from routes.quiz import init_quiz
from routes.password_generator import init_password
from routes.ai_chat import init_ai

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Initialize CORS
CORS(app)

# Setup logging
def setup_logging():
    """Configure logging for the application"""
    if not app.debug:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Application startup")

setup_logging()

# Initialize route modules
init_auth(app)
init_notes(app)
init_quiz(app)
init_password(app)
init_ai(app)

PROTECTED_ROUTES = {"dashboard", "notes", "quiz", "password", "qr", "unit", "text", "ai"}


@app.before_request
def protect_routes():
    if request.endpoint in PROTECTED_ROUTES and not session.get("user_id"):
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))

    if request.endpoint in {"login", "register"} and session.get("user_id"):
        return redirect(url_for("dashboard"))


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    app.logger.warning(f"404 error: {request.url}")
    return render_template("error.html", error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"500 error: {error}")
    return render_template("error.html", error_code=500, error_message="Internal server error"), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    app.logger.warning(f"403 error: {request.url}")
    return render_template("error.html", error_code=403, error_message="Access forbidden"), 403


# ===============================
# Dashboard
# ===============================

@app.route("/")
def dashboard():
    return render_template("dashboard.html", user_name=session.get("name"))

# ===============================
# QR Generator
# ===============================

@app.route("/qr")
def qr():
    return render_template("qr.html")


# ===============================
# Unit Converter
# ===============================

@app.route("/unit")
def unit():
    return render_template("unit.html")


# ===============================
# Text Utilities
# ===============================

@app.route("/text")
def text():
    return render_template("text.html")



if __name__ == "__main__":
    # Get host and port from environment, with sensible defaults
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    app.run(host=host, port=port, debug=debug)