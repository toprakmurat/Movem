from flask import Blueprint, jsonify, request, render_template
from src.config.database import execute_query
from src.services.movie_service import *
from src.services.favorite_service import *

movies_bp = Blueprint('movies', __name__)


######## movies
@movies_bp.route('/', methods=['GET'])
def movies_page():
    """
    Render movies page with pagination and genres for frontend
    URL example: /movies?page=2&per_page=8
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=8, type=int)

    # Paginated movies
    pagination, err_movies = get_movies_paginated_db(page=page, per_page=per_page)
    if err_movies:
        return f"Error fetching movies: {err_movies}", 500

    # Genres
    genres, err_genres = get_genres_db()
    if err_genres:
        return f"Error fetching genres: {err_genres}", 500

    return render_template(
        "movies.html",
        movies=pagination,
        genres=genres
    )

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    """Get a specific movie"""
    movie, err = get_movie_by_id_db(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(movie), 200


@movies_bp.route("/", methods=["POST"])
def create_movie():
    """Get a new movie"""
    movie_data = request.get_json()
    if not movie_data:
        return jsonify({"error": "No data provided"}), 400

    new_movie, err = create_movie_db(movie_data)
    if err:
        return jsonify({"error": err}), 500

    return jsonify(new_movie), 201


@movies_bp.route("/<int:id>", methods=["PUT"])
def update_movie(id):
    """Update movie by id"""
    movie_data = request.get_json()
    if not movie_data:
        return jsonify({"error": "No data provided"}), 400

    updated_movie, err = update_movie_db(id, movie_data)
    if err:
        return jsonify({"error": err}), 500
    if not updated_movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(updated_movie), 200



@movies_bp.route("/<int:id>", methods=["DELETE"])
def delete_movie(id):
    """Delete movie by id"""
    deleted_movie, err = delete_movie_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted_movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(deleted_movie), 200

######## genres
@movies_bp.route("/genres", methods=["GET"])
def get_all_genres():
    """Get all genres"""
    genres, err = get_genres_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(g) for g in genres]), 200


@movies_bp.route("/genre/<int:id>", methods=["GET"])
def get_genre_by_id(id):
    """Get a genre by id"""
    genre, err = get_genres_by_id_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not genre:
        return jsonify({"message": "Genre not found"}), 404
    return jsonify(genre), 200


@movies_bp.route("/genre", methods=["POST"])
def create_genre():
    """Create a new genre"""
    genre_data = request.get_json()
    if not genre_data or 'id' not in genre_data or 'genre_name' not in genre_data:
        return jsonify({"error": "id and genre_name are required"}), 400

    new_genre, err = create_genre_db(genre_data)
    if err:
        return jsonify({"error": err}), 500
    return jsonify(new_genre), 201


@movies_bp.route("/genre/<int:id>", methods=["PUT"])
def update_genre(id):
    """Update genre by id"""
    genre_data = request.get_json()
    if not genre_data:
        return jsonify({"error": "No data provided"}), 400

    updated_genre, err = update_genre_db(id, genre_data)
    if err:
        return jsonify({"error": err}), 500
    if not updated_genre:
        return jsonify({"message": "Genre not found"}), 404
    return jsonify(updated_genre), 200


@movies_bp.route("/genre/<int:id>", methods=["DELETE"])
def delete_genre(id):
    """Delete genre by id"""
    deleted_genre, err = delete_genre_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted_genre:
        return jsonify({"message": "Genre not found"}), 404
    return jsonify(deleted_genre), 200

@movies_bp.route("/genres/<int:genre_id>", methods=["GET"])
def get_movies_by_genre(genre_id):
    """Get movie by genre_id"""
    movies, err = get_movies_by_genre_db(genre_id)
    if err and err == "Genre not found":
        return jsonify({"error": "Genre not found"}), 404
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(movie) for movie in movies]),200

######## movies_genres
@movies_bp.route('/movies-genres', methods=['GET'])
def get_movies_genres():
    """Get all movie-genre relations"""

    movies_genres, err = get_movies_genres_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(movie_genre) for movie_genre in movies_genres]), 200

@movies_bp.route("/movies-genres/<int:id>", methods=["GET"])
def get_movies_genres_by_id(id):
    """Get a movie-genre relation by id"""
    mg, err = get_movies_genres_by_id_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not mg:
        return jsonify({"message": "Movie-Genre relation not found"}), 404
    return jsonify(dict(mg)), 200

@movies_bp.route("/movies-genres", methods=["POST"])
def create_movies_genres():
    """Create a movie-genre relation"""
    data = request.get_json()
    if not data or "movie_id" not in data or "genre_id" not in data:
        return jsonify({"error": "movie_id and genre_id are required"}), 400

    new_mg, err = create_movie_genre_db(data)
    if err:
        return jsonify({"error": err}), 500

    return jsonify(dict(new_mg)), 201

@movies_bp.route("/movies-genres/<int:id>", methods=["PUT"])
def update_movies_genres(id):
    """Update movie-genre relation"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated, err = update_movie_genre_db(id, data)
    if err:
        return jsonify({"error": err}), 500
    if not updated:
        return jsonify({"message": "Movie-Genre relation not found"}), 404

    return jsonify(dict(updated)), 200


@movies_bp.route("/movies-genres/<int:id>", methods=["DELETE"])
def delete_movies_genres(id):
    """Delete movie-genre relation"""
    deleted, err = delete_movie_genre_db(id)
    if err and err == "Not found":
        return jsonify({"message": "Movie-Genre relation not found"}), 404
    if err:
        return jsonify({"error": err}), 500

    return jsonify(dict(deleted)), 200

#########favorites
@movies_bp.route("/favorites", methods=["GET"])
def get_favorites():
    favorites, err = get_favorites_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(f) for f in favorites]), 200


@movies_bp.route("/favorites/<int:id>", methods=["GET"])
def get_favorite(id):
    fav, err = get_favorite_by_id_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not fav:
        return jsonify({"message": "Favorite not found"}), 404
    return jsonify(fav), 200


@movies_bp.route("/favorites", methods=["POST"])
def create_favorite():
    data = request.get_json()
    if not data or "user_id" not in data or "movie_id" not in data:
        return jsonify({"error": "user_id and movie_id required"}), 400

    fav, err = create_favorite_db(data)
    if err:
        return jsonify({"error": err}), 500

    return jsonify(fav), 201


@movies_bp.route("/favorites/<int:id>", methods=["PUT"])
def update_favorite(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated, err = update_favorite_db(id, data)
    if err:
        return jsonify({"error": err}), 500
    if not updated:
        return jsonify({"message": "Favorite not found"}), 404

    return jsonify(updated), 200


@movies_bp.route("/favorites/<int:id>", methods=["DELETE"])
def delete_favorite(id):
    deleted, err = delete_favorite_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted:
        return jsonify({"message": "Favorite not found"}), 404

    return jsonify(deleted), 200

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
