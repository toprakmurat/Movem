from flask import Flask
from src.config.database import db
from src.routes.home import home_bp
from src.routes.movies import movies_bp
from src.routes.actors import actors_bp


def create_app():
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movem.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(movies_bp, url_prefix='/movies')
    app.register_blueprint(actors_bp, url_prefix='/actors')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)