"""WSGI entry point for production servers (Gunicorn, etc.)"""
import os
from app import app

if __name__ == "__main__":
    app.run()
