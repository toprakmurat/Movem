import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Flask configuration class"""
    
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # PostgreSQL Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'movem')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    print(DB_USER)
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    
    # Connection pool settings
    DB_MIN_CONNECTIONS = int(os.environ.get('DB_MIN_CONNECTIONS', '1'))
    DB_MAX_CONNECTIONS = int(os.environ.get('DB_MAX_CONNECTIONS', '20'))
    
    # Construct DATABASE_URL from individual components
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # JSON configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
