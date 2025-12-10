from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from src.services.comments_service import (
    get_all_comments,
    get_comment_by_id,
    create_comment,
    update_comment,
    delete_comment_by_id,
    get_comments_for_movie,
    get_comments_for_movie_sorted,
    like_comment,
    dislike_comment,
    toggle_comment_vote_db,
    get_user_vote_status
)

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
def like_comment_route(comment_id):
    updated, err = like_comment(comment_id)
    if err:
        if err == "Comment not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify(dict(updated)), 200

    
@comments_bp.route('/<int:comment_id>/dislike', methods=['POST'])
def dislike_comment_route(comment_id):
    updated, err = dislike_comment(comment_id)
    if err:
        if err == "Comment not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify(dict(updated)), 200


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