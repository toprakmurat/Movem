from flask import Blueprint, jsonify, request
from src.config.database import execute_query
from src.services.movie_service import (
    get_movies,
    get_movie_by_id,
    create_movie,
    update_movie,
    delete_movie_by_id,
    get_movies_by_genre_id,
    get_platforms,
    get_platform_by_id,
    create_platform,
    update_platform,
    delete_platform_by_id
)

movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/', methods=['GET'])
def get_movies():
    """Get all movies"""

    movies, err = get_movies()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(movie) for movie in movies]), 200


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie"""
    movie, err = get_movie_by_id(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(movie), 200


@movies_bp.route("/", methods=["POST"])
def create_new_movie():
    """Get a new movie"""
    movie_data = request.get_json()
    if not movie_data:
        return jsonify({"error": "No data provided"}), 400

    new_movie, err = create_movie(movie_data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_movie)), 201


@movies_bp.route("/<int:id>", methods=["PUT"])
def update_existing_movie(id):
    """Update movie by id"""
    movie_data = request.get_json()
    if not movie_data:
        return jsonify({"error": "No data provided"}), 400

    updated_movie, err = update_movie(id, movie_data)
    if err:
        return jsonify({"error": err}), 400
    if not updated_movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(dict(updated_movie)), 200



@movies_bp.route("/<int:id>", methods=["DELETE"])
def delete_movie(id):
    """Delete movie by id"""
    deleted_movie, err = delete_movie_by_id(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted_movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(dict(deleted_movie)), 200


@movies_bp.route("/genre/<int:genre_id>", methods=["GET"])
def get_movies_by_genre(genre_id):
    """Get movie by genre_id"""
    movies, err = get_movies_by_genre_id(genre_id)
    if err:
        return jsonify({"error": err}), 500
    if not movies:
        return jsonify({"message": f"No movies found for genre {genre_id}"}), 404
    return jsonify([dict(movie) for movie in movies]),200

# Platforms CRUD operations

@movies_bp.route('/platforms/', methods=['GET'])
def get_all_platforms_route():
    """Gets all platforms"""
    platforms, err = get_platforms()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(p) for p in platforms]), 200


@movies_bp.route('/platforms/<int:platform_id>', methods=['GET'])
def get_platform_route(platform_id):
    """Gets a single platform by its ID"""
    platform, err = get_platform_by_id(platform_id)
    if err:
        if err == "Platform not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify(dict(platform)), 200


@movies_bp.route('/platforms/', methods=['POST'])
def create_platform_route():
    """Creates a new platform"""
    data = request.get_json()
    if not data or 'platform_name' not in data:
        return jsonify({'error': 'platform_name is required'}), 400
        
    new_platform, err = create_platform(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_platform)), 201


@movies_bp.route('/platforms/<int:platform_id>', methods=['PUT', 'PATCH'])
def update_platform_route(platform_id):
    """Updates an existing platform"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    updated, err = update_platform(platform_id, data)
    
    if err:
        if err == "Platform not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 400
        
    return jsonify(dict(updated)), 200


@movies_bp.route('/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform_route(platform_id):
    """Deletes a platform"""
    deleted, err = delete_platform_by_id(platform_id)
    
    if err:
        if err == "Platform not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
        
    return jsonify(dict(deleted)), 200