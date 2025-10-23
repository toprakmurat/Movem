from flask import Blueprint, jsonify
from src.config.database import execute_query

movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/', methods=['GET'])
def get_movies():
    """Get all movies"""
    try:
        movies = execute_query(
            "SELECT * FROM movies",
            fetch=True
        )
        return jsonify([dict(movie) for movie in movies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie"""
    try:
        movie = execute_query(
            "SELECT * FROM movies WHERE id = %s",
            (movie_id),
            fetch=True
        )
        if movie:
            return jsonify(dict(movie[0]))
        return jsonify({'error': 'Movie not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500