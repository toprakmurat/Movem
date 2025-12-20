from flask import Blueprint, jsonify, request, render_template
from flask_login import current_user, login_required
from src.services.comments_service import (
    get_all_comments,
    get_comment_by_id,
    create_comment,
    update_comment,
    delete_comment_by_id,
    get_comments_for_movie,
    get_comments_for_movie_sorted,
    toggle_comment_vote_db,
    get_user_vote_status,
    create_vote,
    update_vote,
    delete_vote,
    get_vote_by_user_and_comment,
    get_controversial_movies
)
from src.services.movie_service import get_movies_paginated_db


comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/', methods=['GET'])
def get_all_comments_route():
    comments, err = get_all_comments()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(c) for c in comments]), 200

    
@comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_comment_route(comment_id):
    comment, err = get_comment_by_id(comment_id)
    if err:
        if err == "Comment not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify(dict(comment)), 200

    
@comments_bp.route('/', methods=['POST'])
def create_comment_route():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()
        if "has_spoiler" in data:
            data["has_spoiler"] = data["has_spoiler"] in ["1", "true", "on", True]
    if 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    if isinstance(data['rating'], str):
        data['rating'] = int(data['rating']) if data['rating'].isdigit() else None
    new_comment, err = create_comment(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_comment)), 201

    
@comments_bp.route('/<int:comment_id>', methods=['PUT', 'PATCH'])
@login_required
def update_comment_route(comment_id):
    comment, err = get_comment_by_id(comment_id)
    if err:
        return jsonify({"message": "Comment not found"}), 404       
    if comment['user_id'] != current_user.id:
        return jsonify({"error": "Unauthorized: You can only edit your own comments"}), 403
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400    
    updated, err = update_comment(comment_id, data)
    if err:
        return jsonify({"error": err}), 400   
    return jsonify(dict(updated)), 200


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment_route(comment_id):
    comment, err = get_comment_by_id(comment_id)
    if err:
        return jsonify({"message": "Comment not found"}), 404
    if comment['user_id'] != current_user.id:
        return jsonify({"error": "Unauthorized: You can only delete your own comments"}), 403
    deleted, err = delete_comment_by_id(comment_id)  
    if err:
        return jsonify({"error": err}), 500     
    return jsonify(dict(deleted)), 200


@comments_bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_comments_for_movie_route(movie_id):
    comments, err = get_comments_for_movie(movie_id)
    if err:
        if err == "No comments found for this movie":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify([dict(c) for c in comments]), 200

    
@comments_bp.route('/movie/<int:movie_id>/best', methods=['GET'])
def get_comments_best_route(movie_id):
    comments, err = get_comments_for_movie_sorted(movie_id, sort_order="DESC")
    if err:
        if err == "No rated comments found for this movie":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify([dict(c) for c in comments]), 200

    
@comments_bp.route('/movie/<int:movie_id>/worst', methods=['GET'])
def get_comments_worst_route(movie_id):
    comments, err = get_comments_for_movie_sorted(movie_id, sort_order="ASC")
    if err:
        if err == "No rated comments found for this movie":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify([dict(c) for c in comments]), 200


@comments_bp.route('/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment_route(comment_id):
    """
    Refactored for 3NF: Uses toggle_comment_vote_db instead of deprecated column updates.
    Requires login because user_id is mandatory for the votes table.
    """
    result, err = toggle_comment_vote_db(current_user.id, comment_id, 'like')
    if err:
        return jsonify({"error": err}), 500
    return jsonify(result), 200

    
@comments_bp.route('/<int:comment_id>/dislike', methods=['POST'])
@login_required
def dislike_comment_route(comment_id):
    """
    Refactored for 3NF: Uses toggle_comment_vote_db instead of deprecated column updates.
    Requires login because user_id is mandatory for the votes table.
    """
    result, err = toggle_comment_vote_db(current_user.id, comment_id, 'dislike')
    if err:
        return jsonify({"error": err}), 500
    return jsonify(result), 200


@comments_bp.route('/<int:comment_id>/vote', methods=['POST'])
def vote_comment_route(comment_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login required'}), 401  
    data = request.get_json()
    vote_type = data.get('vote_type', 'like')
    result, err = toggle_comment_vote_db(current_user.id, comment_id, vote_type)
    if err:
        return jsonify({'error': err}), 500
    updated_comment, _ = get_comment_by_id(comment_id)
    comment_data = dict(updated_comment)
    status = get_user_vote_status(current_user.id, comment_id)
    
    return jsonify({
        'success': True,
        'likes': comment_data.get('comment_likes', 0),
        'dislikes': comment_data.get('comment_dislikes', 0),
        'user_status': status
    }), 200


@comments_bp.route('/battleground', methods=['GET', 'POST'])
def battleground_page():
    """
    Renders the 'Polarization Matrix' page.
    GET: Shows top 6 controversial movies.
    POST: Handles 'Manual Targeting' search to analyze a specific movie.
    """
    movies, err = get_controversial_movies()
    top_movies = [dict(m) for m in movies] if (not err and movies) else []
    searched_movie = None
    search_error = False
    
    if request.method == 'POST':
        query = request.form.get('search_query')
        if query:
            result, err = get_movies_paginated_db(page=1, per_page=1, search=query)
            found_items = []
            if hasattr(result, 'items'):
                found_items = result.items
            elif isinstance(result, dict) and 'items' in result:
                found_items = result['items']
            elif isinstance(result, list): 
                found_items = result
            
            if found_items:
                movie = found_items[0]
                movie_dict = dict(movie) if not isinstance(movie, dict) else movie.copy()
                comments, _ = get_comments_for_movie(movie_dict['id'])
                if not comments: comments = []
                
                total_comments = len(comments)
                interactions = 0
                ratings = []
                
                for c in comments:
                    c_dict = dict(c)
                    likes = c_dict.get('comment_likes') or 0
                    dislikes = c_dict.get('comment_dislikes') or 0
                    interactions += (likes + dislikes)
                    if c_dict.get('rating') is not None:
                        ratings.append(float(c_dict['rating']))
                
                if len(ratings) > 1:
                    mean = sum(ratings) / len(ratings)
                    variance = sum((x - mean) ** 2 for x in ratings) / len(ratings)
                    score = variance
                else:
                    score = 0.0
                
                movie_dict['movie_id'] = movie_dict['id']
                movie_dict['total_comments'] = total_comments
                movie_dict['community_tension'] = interactions
                movie_dict['polarization_score'] = round(score, 2) 
                searched_movie = movie_dict
            else:
                search_error = True
                
    return render_template(
        'battleground.html', 
        movies=top_movies, 
        searched_movie=searched_movie, 
        search_error=search_error
    )

# --- COMMENT VOTES ROUTES (ADMIN & API) ---

@comments_bp.route('/votes', methods=['GET'])
@login_required
def get_vote_route():
    """
    Get a single vote by user_id and comment_id (Query params)
    """
    user_id = request.args.get('user_id')
    comment_id = request.args.get('comment_id')
    
    if not user_id or not comment_id:
        return jsonify({"error": "Missing user_id or comment_id params"}), 400

    vote, err = get_vote_by_user_and_comment(user_id, comment_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(dict(vote)), 200


@comments_bp.route('/votes', methods=['POST'])
@login_required
def create_vote_route():
    """
    Directly create a vote record. 
    Returns a success message instead of the object to prevent date serialization errors.
    """
    data = request.get_json()
    comment_id = data.get('comment_id')
    vote_type = data.get('vote_type')
    
    target_user_id = data.get('user_id', current_user.id)

    if not comment_id or not vote_type:
        return jsonify({'error': 'Missing comment_id or vote_type'}), 400
    
    if vote_type not in ['like', 'dislike']:
        return jsonify({'error': 'Invalid vote type'}), 400

    new_vote, err = create_vote(target_user_id, comment_id, vote_type)
    
    if err:
        if "already voted" in str(err) or "unique" in str(err) or "duplicate" in str(err):
             return jsonify({"error": "This user has already voted on this comment."}), 409
        return jsonify({"error": err}), 400
    
    return jsonify({"message": "Vote created successfully", "success": True}), 201


@comments_bp.route('/votes', methods=['PUT', 'PATCH'])
@login_required
def update_vote_route():
    """
    Update a vote (e.g., change 'like' to 'dislike').
    Returns a success message instead of the object to prevent date serialization errors.
    """
    data = request.get_json()
    try:
        user_id = int(data.get('user_id'))
        comment_id = int(data.get('comment_id'))
    except (TypeError, ValueError):
        return jsonify({"error": "User ID and Comment ID must be numbers"}), 400
        
    new_type = data.get('vote_type')

    if not new_type:
        return jsonify({"error": "Missing vote_type"}), 400

    if new_type not in ['like', 'dislike']:
        return jsonify({"error": "Invalid vote type"}), 400

    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    updated_vote, err = update_vote(user_id, comment_id, new_type)
    if err:
        return jsonify({"error": err}), 500
    
    return jsonify({"message": "Vote updated successfully", "success": True}), 200


@comments_bp.route('/votes', methods=['DELETE'])
@login_required
def delete_vote_route():
    """
    Delete a vote permanently using user_id and comment_id.
    Returns a success message instead of the object to prevent date serialization errors.
    """
    user_id = request.args.get('user_id')
    comment_id = request.args.get('comment_id')

    if not (user_id and comment_id):
        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

    if not user_id or not comment_id:
        return jsonify({"error": "Missing user_id or comment_id"}), 400

    if int(user_id) != current_user.id and current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    deleted, err = delete_vote(user_id, comment_id)
    if err:
        return jsonify({"error": err}), 500
        
    return jsonify({"message": "Vote deleted successfully", "success": True}), 200