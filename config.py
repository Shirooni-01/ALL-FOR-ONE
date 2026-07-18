import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE = os.path.join(os.path.dirname(__file__), "users.db")
    JSON_DATABASE = os.path.join(os.path.dirname(__file__), "notes.json")
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 days
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # CORS configuration
    CORS_HEADERS = "Content-Type"
    
    # API Keys (should be in environment variables)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Enforce HTTPS and security
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE = ":memory:"
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
