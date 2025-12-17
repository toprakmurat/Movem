from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from src.config.database import execute_query
from src.services.movie_service import *
from src.services.genres_service import *
from src.services.favorite_service import *
from flask_login import current_user
from src.services.comments_service import get_comments_for_movie
from src.services.list_service import get_lists_by_user_db
from src.utils.file_utils import save_upload_file, delete_file
from src.utils.decorators import admin_required

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

    search = request.args.get("search", type=str)
    genre_id = request.args.get("genre", type=int)
    sort_by = request.args.get("sort")
    
    rating_min = request.args.get("rating_min", default=0, type=float)
    rating_max = request.args.get("rating_max", default=10, type=float)
    runtime_min = request.args.get("runtime_min", default=0, type=int)
    runtime_max = request.args.get("runtime_max", default=300, type=int)
    
    is_ajax = request.args.get('ajax', type=int) == 1
    fmt = request.args.get('format', type=str)

    # Paginated movies  
    pagination, err_movies = get_movies_paginated_db(
        page=page, 
        per_page=per_page, 
        genre_id=genre_id, 
        sort_by=sort_by,
        search=search,
        rating_min=rating_min,
        rating_max=rating_max,
        runtime_min=runtime_min,
        runtime_max=runtime_max
    )
    if err_movies:
        if is_ajax:
             return jsonify({'error': str(err_movies)}), 500
        return f"Error fetching movies: {err_movies}", 500

    if fmt == 'json':
        return jsonify({
            'items': [dict(m) for m in pagination.items],
            'pagination': {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }
        })

    if is_ajax:

        movies_html = []
        for movie in pagination.items:
            movies_html.append(render_template('partials/movie_card.html', movie=movie))
        
        return jsonify({
            'html': ''.join(movies_html),
            'pagination': {
                'total': pagination.total,
                'start_index': pagination.start_index(),
                'end_index': pagination.end_index(),
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num,
                'page': page
            }
        })

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
def movies_details_page(movie_id):
    """ Returns corresponding page for movies """
    fmt = request.args.get("format", type=str)
    
    if fmt == 'json':
        movie, err = get_movie_by_id_db(movie_id)
        if err:
            return jsonify({"error": err}), 500
        if not movie:
            return jsonify({"message": "Movie not found"}), 404
            
        return jsonify(dict(movie))

    current_uid = current_user.id if current_user.is_authenticated else None
    movie_detail, err = get_movie_details_full_db(movie_id, current_uid)

    if err:
        return f"Error fetching movie details: {err}", 500

    if not movie_detail:
        return "Movie not found", 404

    director = get_movie_director(movie_id)
    cast_list = get_movie_actors(movie_id, limit=15)

    all_comments, comm_err = get_comments_for_movie(movie_id, user_id=current_uid)
    all_comments = all_comments or []

    similar_movies_list = get_recommendations_db(movie_id, current_uid)

    user_lists = []
    if current_user.is_authenticated:
        from src.services.list_service import get_list_details_db
        lists_data, list_err = get_lists_by_user_db(current_uid)
        if not list_err and lists_data:
            # Fetch full details including movies for each list
            for lst in lists_data:
                list_details, _ = get_list_details_db(lst['id'])
                if list_details:
                    user_lists.append({
                        'id': lst['id'],
                        'list_name': lst['list_name'],
                        'movies': list_details.get('movies', [])
                    })

    movie_detail["user_lists"] = user_lists
    movie_detail["similar_movies"] = similar_movies_list
    movie_detail["director"] = director
    movie_detail["cast"] = cast_list
    movie_detail["reviews"] = all_comments
    movie_detail["total_reviews_count"] = len(all_comments)

    return render_template("movie_detail.html", **movie_detail)


@movies_bp.route('/<int:movie_id>/favorite', methods=['POST'])
def toggle_favorite(movie_id):
    if not current_user.is_authenticated:
        return jsonify({"message": "You need to login to add favorites."}), 401

    result, error = toggle_favorite_db(current_user.id, movie_id)

    if error:
        return jsonify({"error": error}), 500

    action = result["action"]
    message = "Added to favorites" if action == "added" else "Removed from favorites"

    return redirect(url_for('movies.movies_details_page', movie_id=movie_id))


@movies_bp.route("/", methods=["POST"])
@admin_required
def create_movie():
    """Get a new movie"""
    data = {}
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # File uploads
    if 'poster_file' in request.files:
        fn = save_upload_file(request.files['poster_file'])
        if fn: data['poster_file'] = fn
        
    if 'banner_file' in request.files:
        fn = save_upload_file(request.files['banner_file'])
        if fn: data['banner_file'] = fn

    new_movie, err = create_movie_db(data)
    if err:
        return jsonify({"error": err}), 500

    return jsonify(new_movie), 201


@movies_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_movie(id):
    """Update movie by id"""
    data = {}
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    if not data and not request.files:
        return jsonify({"error": "No data provided"}), 400

    # File uploads
    if 'poster_file' in request.files:
        fn = save_upload_file(request.files['poster_file'])
        if fn: data['poster_file'] = fn

    if 'banner_file' in request.files:
        fn = save_upload_file(request.files['banner_file'])
        if fn: data['banner_file'] = fn

    updated_movie, err = update_movie_db(id, data)
    if err:
        return jsonify({"error": err}), 500
    if not updated_movie:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(updated_movie), 200



@movies_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_movie(id):
    """Delete movie by id"""
    movie, err = get_movie_by_id_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not movie:
        return jsonify({"message": "Movie not found"}), 404

    # Delete the movie record
    deleted_movie, err = delete_movie_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted_movie:
        return jsonify({"message": "Movie not found"}), 404
        
    delete_file(movie.get('poster_file'))
    delete_file(movie.get('banner_file'))
    
    return jsonify(deleted_movie), 200

######## genres
@movies_bp.route("/genres", methods=["GET"])
def get_all_genres():
    """Get all genres with optional pagination"""
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    if page:
        paginated, err = get_genres_paginated_db(page, per_page)
        if err:
            return jsonify({"error": err}), 500
        return jsonify({
            'items': [dict(g) for g in paginated.items],
            'pagination': {
                'total': paginated.total,
                'page': paginated.page,
                'per_page': paginated.per_page,
                'pages': paginated.pages
            }
        }), 200
    
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
@admin_required
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
@admin_required
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
@admin_required
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
    """Get all movie-genre relations with optional pagination"""
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    if page:
        paginated, err = get_movies_genres_paginated_db(page, per_page)
        if err:
            return jsonify({"error": err}), 500
        return jsonify({
            'items': [dict(mg) for mg in paginated.items],
            'pagination': {
                'total': paginated.total,
                'page': paginated.page,
                'per_page': paginated.per_page,
                'pages': paginated.pages
            }
        }), 200

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
@admin_required
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
@admin_required
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
@admin_required
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
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    if page:
        paginated, err = get_favorites_paginated_db(page, per_page)
        if err:
            return jsonify({"error": err}), 500
        return jsonify({
            'items': [dict(f) for f in paginated.items],
            'pagination': {
                'total': paginated.total,
                'page': paginated.page,
                'per_page': paginated.per_page,
                'pages': paginated.pages
            }
        }), 200

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
@admin_required
def create_favorite():
    data = request.get_json()
    if not data or "user_id" not in data or "movie_id" not in data:
        return jsonify({"error": "user_id and movie_id required"}), 400

    fav, err = create_favorite_db(data)
    if err:
        return jsonify({"error": err}), 500

    return jsonify(fav), 201


@movies_bp.route("/favorites/<int:id>", methods=["PUT"])
@admin_required
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
@admin_required
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

# Routes reviews page from movie page

@movies_bp.route('/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews_page(movie_id):
    movie, err = get_movie_by_id_db(movie_id)
    if not movie:
        return render_template("404.html"), 404
    sort_by = request.args.get('sort', 'newest')
    spoiler_filter = request.args.get('spoiler', 'all')
    current_uid = current_user.id if current_user.is_authenticated else None
    all_reviews, _ = get_comments_for_movie(
        movie_id, 
        sort_by=sort_by, 
        spoiler_filter=spoiler_filter, 
        user_id=current_uid 
    )
    if not all_reviews:
        all_reviews = []
    page = request.args.get('page', 1, type=int)
    class SimplePagination:
        def __init__(self, items, page, per_page):
            self.total = len(items)
            self.page = page
            self.per_page = per_page
            start = (page - 1) * per_page
            end = start + per_page
            self.items = items[start:end]

        @property
        def has_prev(self): 
            return self.page > 1
            
        @property
        def has_next(self): 
            return (self.page * self.per_page) < self.total
            
        @property
        def prev_num(self): 
            return self.page - 1
            
        @property
        def next_num(self): 
            return self.page + 1
            
        def start_index(self): 
            return ((self.page - 1) * self.per_page) + 1 if self.total > 0 else 0
            
        def end_index(self): 
            return min(self.page * self.per_page, self.total)

    pagination = SimplePagination(all_reviews, page=page, per_page=20)

    return render_template(
        "comments.html",
        movie=movie,
        reviews=pagination,
        current_sort=sort_by,
        current_spoiler=spoiler_filter,
        user_votes={} 
    )