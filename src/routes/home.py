from flask import Blueprint, jsonify

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    """Movem home endpoint"""
    return jsonify({
        'message': 'Welcome to Movem API',
        'endpoints': {
            'movies': '/movies',
            'actors': '/actors'
        }
    })