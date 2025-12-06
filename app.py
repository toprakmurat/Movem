from flask import Flask
import psycopg2
from psycopg2 import pool
import os
from flask_login import LoginManager
from src.models.user_model import User
from src.services.users_service import get_user_by_id_db
from src.routes.auth import auth_bp
from config import config
from src.routes.home import home_bp
from src.routes.movies import movies_bp
from src.routes.actors import actors_bp
from src.routes.comments import comments_bp
from src.routes.game import game_bp
from src.routes.statistic import statistic_bp

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
    # Flask login setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Her istekte kullanıcıyı veritabanından yükler
        user_data, _ = get_user_by_id_db(int(user_id))
        if user_data:
            return User(user_data)
        return None
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp, url_prefix='/movies')
    app.register_blueprint(actors_bp, url_prefix='/actors')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(statistic_bp, url_prefix='/statistic')
    
    @app.teardown_appcontext
    def teardown_db(exception):
        from src.config.database import close_db_connection
        close_db_connection()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5050, debug=True)