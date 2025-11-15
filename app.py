from flask import Flask
import psycopg2
from psycopg2 import pool
import os
from config import config
from src.routes.home import home_bp
from src.routes.movies import movies_bp
from src.routes.actors import actors_bp
from src.routes.comments import comments_bp
from src.routes.platforms import platforms_bp

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize database connection pool
    try:
        app.db_pool = psycopg2.pool.SimpleConnectionPool(
            app.config['DB_MIN_CONNECTIONS'],
            app.config['DB_MAX_CONNECTIONS'],
            app.config['DATABASE_URL']
        )
        print(f"Database connection pool created successfully")
    except Exception as e:
        print(f"Error creating database pool: {e}")
        app.db_pool = None
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(movies_bp, url_prefix='/movies')
    app.register_blueprint(actors_bp, url_prefix='/actors')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    app.register_blueprint(platforms_bp, url_prefix='/platforms')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5050, debug=True)