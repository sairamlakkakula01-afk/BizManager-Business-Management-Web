import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')


class BaseConfig:
    """Base configuration settings shared across environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-secret-key-change-in-production-37482910')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}
    
    # Rate limiter
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '500 per day; 100 per hour')
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    # Ensure instance directory exists
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(instance_path, 'bizmanager.db')}"
    )


class TestingConfig(BaseConfig):
    """Testing configuration with in-memory database and fast tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration with strict security flags."""
    DEBUG = False
    TESTING = False
    # In production, require an explicitly set SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
