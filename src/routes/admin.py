from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from src.utils.pagination_utils import Pagination

from src.services.users_service import (
    get_users_db,
    get_user_by_id_db,
    create_user_db,
    update_user_db,
    delete_user_db,
    get_user_by_username_db,
    get_users_by_role_db,
    get_user_by_email_db,
    get_user_favorite_genre_stats_db,
    get_user_favorite_actor_stats_db,
    get_most_active_curators_db
)

from src.services.list_service import (
    create_custom_list_db,
    get_lists_by_user_db,
    delete_list_db,
    add_movie_to_list_db,
    remove_movie_from_list_db,
    get_list_details_db
)

from src.services.movie_service import get_movies_paginated_db, get_movies_db
from src.services.genres_service import (
    get_genres_paginated_db,
    get_movies_genres_paginated_db,
    get_genres_db,
    get_movies_genres_db
)

from src.services.comments_service import (
    get_all_comments_detailed, 
    delete_comment_by_id, 
    toggle_spoiler_status,
    get_all_votes_detailed,
    delete_vote,
    get_comment_by_id,
    get_vote_by_id
)

from src.services.actors_service import get_actors_paginated_db

from src.services.statistic_service import get_statistics_paginated_db

from src.services.game_service import get_questions_paginated_db

from src.services.favorite_service import get_favorites_paginated_db, get_favorites_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('home.home'))

@admin_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    # Role filter for users
    role_filter = request.args.get('role_filter', '')
    
    # Context data to show on the dashboard
    if role_filter and role_filter != 'all':
        users, _ = get_users_by_role_db(role_filter)
    else:
        users, _ = get_users_db()
    
    active_curators, _ = get_most_active_curators_db()
    
    # Pagination Parameters
    movies_page = request.args.get('movies_page', 1, type=int)
    genres_page = request.args.get('genres_page', 1, type=int)
    mg_page = request.args.get('mg_page', 1, type=int)
    fav_page = request.args.get('fav_page', 1, type=int)
    per_page = 100

    # Fetch paginated data
    movies_paginated, _ = get_movies_paginated_db(page=movies_page, per_page=per_page)
    genres_paginated, _ = get_genres_paginated_db(page=genres_page, per_page=per_page)
    movies_genres_paginated, _ = get_movies_genres_paginated_db(page=mg_page, per_page=per_page)
    favorites_paginated, _ = get_favorites_paginated_db(page=fav_page, per_page=per_page)

    # Others (non-paginated or pre-limited)
    actors_result, _ = get_actors_paginated_db(page=1, per_page=1000)
    actors = actors_result['actors'] if actors_result else []
    
    # Paginated Statistics and Game Questions
    stats_page = request.args.get('stats_page', 1, type=int)
    game_page = request.args.get('game_page', 1, type=int)
    
    statistics_paginated, _ = get_statistics_paginated_db(page=stats_page, per_page=per_page)
    questions_paginated, _ = get_questions_paginated_db(page=game_page, per_page=per_page)

    # Placeholders for search results
    selected_user = None
    selected_list = None
    user_stats = {}
    genre_stats = None
    actor_stats = None
    
    # Handle simple lookups via GET parameters (for result persistence after action)
    if request.args.get('view_user_id'):
        uid = int(request.args.get('view_user_id'))
        selected_user, _ = get_user_by_id_db(uid)
        if selected_user:
            genre_stats, _ = get_user_favorite_genre_stats_db(uid)
            actor_stats = get_user_favorite_actor_stats_db(uid)

    if request.args.get('view_list_id'):
        lid = int(request.args.get('view_list_id'))
        selected_list, _ = get_list_details_db(lid)

    return render_template(
        'admin/dashboard.html',
        users=users,
        active_curators=active_curators,
        selected_user=selected_user,
        selected_list=selected_list,
        genre_stats=genre_stats,
        actor_stats=actor_stats,
        movies=movies_paginated,
        genres=genres_paginated,
        movies_genres=movies_genres_paginated,
        actors=actors,
        statistics=statistics_paginated,
        questions=questions_paginated,
        favorites=favorites_paginated,
        role_filter=role_filter
    )

# --- USER MANAGEMENT ROUTES ---

@admin_bp.route('/user/create', methods=['POST'])
def create_user():
    user_data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'password_hash': generate_password_hash(request.form.get('password')),
        'profile_picture': 'img/placeholder_avatar.svg'
    }
    
    new_user, err = create_user_db(user_data)
    if err:
        flash(f'Error creating user: {err}', 'error')
    else:
        flash(f'User {new_user["username"]} created successfully.', 'success')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/update', methods=['POST'])
def update_user():
    user_id = int(request.form.get('user_id'))
    update_data = {}
    
    # Only add fields that are provided
    if request.form.get('first_name'): update_data['first_name'] = request.form.get('first_name')
    if request.form.get('last_name'): update_data['last_name'] = request.form.get('last_name')
    if request.form.get('bio'): update_data['bio'] = request.form.get('bio')
    if request.form.get('username'): update_data['username'] = request.form.get('username')
    
    updated, err = update_user_db(user_id, update_data)
    if err:
        flash(f'Error updating user: {err}', 'error')
    else:
        flash('User updated successfully.', 'success')
        
    return redirect(url_for('admin.dashboard', view_user_id=user_id))

@admin_bp.route('/user/delete', methods=['POST'])
def delete_user():
    user_id = int(request.form.get('user_id'))
    deleted, err = delete_user_db(user_id)
    
    if err:
        flash(f'Error deleting user: {err}', 'error')
    else:
        flash('User deleted successfully.', 'success')
        
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/lookup', methods=['POST'])
def lookup_user():
    # Helper to find ID from various inputs and redirect to view_user_id
    method = request.form.get('method')
    value = request.form.get('value')
    
    found_user = None
    
    if method == 'id':
        found_user, _ = get_user_by_id_db(int(value))
    elif method == 'username':
        found_user, _ = get_user_by_username_db(value)
    elif method == 'email':
        found_user, _ = get_user_by_email_db(value)
        
    if found_user:
        return redirect(url_for('admin.dashboard', view_user_id=found_user['id']))
    else:
        flash('User not found.', 'error')
        return redirect(url_for('admin.dashboard'))

# --- LIST MANAGEMENT ROUTES ---

@admin_bp.route('/list/create', methods=['POST'])
def create_list():
    user_id = int(request.form.get('user_id'))
    name = request.form.get('list_name')
    is_public = True if request.form.get('is_public') else False
    
    new_list, err = create_custom_list_db(user_id, name, is_public)
    if err:
        flash(f'Error creating list: {err}', 'error')
    else:
        flash(f'List "{name}" created successfully.', 'success')
        
    return redirect(url_for('admin.dashboard', view_user_id=user_id)) # View user to see their lists (not implemented in view yet but consistent)

@admin_bp.route('/list/delete', methods=['POST'])
def delete_list():
    list_id = int(request.form.get('list_id'))
    # For admin delete, we might need a workaround as delete_list_db requires user_id owner check.
    # But as admin we should be able to delete any list. 
    # Current service: delete_list_db(list_id, user_id) Checks owner.
    # To bypass, we first get the list to find the owner.
    
    list_details, err = get_list_details_db(list_id)
    if not list_details:
        flash('List not found.', 'error')
        return redirect(url_for('admin.dashboard'))
        
    owner_id = list_details['list_info']['user_id']
    deleted, err = delete_list_db(list_id, owner_id)
    
    if err:
        flash(f'Error deleting list: {err}', 'error')
    else:
        flash('List deleted successfully.', 'success')
        
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/list/add-movie', methods=['POST'])
def add_movie():
    list_id = int(request.form.get('list_id'))
    movie_id = int(request.form.get('movie_id'))
    
    _, err = add_movie_to_list_db(list_id, movie_id)
    if err:
        flash(f'Error: {err}', 'error')
    else:
        flash('Movie added to list.', 'success')
        
    return redirect(url_for('admin.dashboard', view_list_id=list_id))

@admin_bp.route('/list/remove-movie', methods=['POST'])
def remove_movie():
    list_id = int(request.form.get('list_id'))
    movie_id = int(request.form.get('movie_id'))
    
    _, err = remove_movie_from_list_db(list_id, movie_id)
    if err:
        flash(f'Error: {err}', 'error')
    else:
        flash('Movie removed from list.', 'success')
        
    return redirect(url_for('admin.dashboard', view_list_id=list_id))

@admin_bp.route('/list/view', methods=['POST'])
def view_list():
    # Simple redirect helper
    list_id = request.form.get('list_id')
    return redirect(url_for('admin.dashboard', view_list_id=list_id))

@admin_bp.route('/api/comments', methods=['GET'])
def api_get_comments():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search_query = request.args.get('search', '')
    
    comments, total = get_all_comments_detailed(page, per_page, search_query)
    
    items = []
    if comments:
        for c in comments:
            items.append({
                'id': c['id'],
                'user_id': c['user_id'],
                'username': c['username'],
                'movie_id': c['movie_id'],
                'movie_title': c['movie_title'],
                'body': c['body'],
                'rating': c['rating'],
                'has_spoiler': c['has_spoiler'],
                'comment_likes': c.get('comment_likes', 0),
                'comment_dislikes': c.get('comment_dislikes', 0),
                'created_at': c['created_at'].strftime('%Y-%m-%d %H:%M') if c['created_at'] else '-'
            })
            
    return jsonify({
        'items': items,
        'pagination': {
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page
        }
    })

@admin_bp.route('/api/comments/<int:id>', methods=['GET'])
def api_get_comment_by_id(id):
    comment, err = get_comment_by_id(id)
    if err: return jsonify({'error': err}), 404
    return jsonify(dict(comment))

@admin_bp.route('/api/comments/<int:id>', methods=['DELETE'])
def api_delete_comment(id):
    success, err = delete_comment_by_id(id)
    if err: return jsonify({'error': err}), 400
    return jsonify({'success': True}), 200

@admin_bp.route('/api/comments/toggle-spoiler', methods=['POST'])
def api_toggle_spoiler():
    data = request.get_json()
    comment_id = data.get('id')
    if not comment_id: return jsonify({'error': 'ID required'}), 400
    
    success, err = toggle_spoiler_status(comment_id)
    if not success: return jsonify({'error': err}), 400
    return jsonify({'success': True}), 200

@admin_bp.route('/api/votes', methods=['GET'])
def api_get_votes():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    votes, total = get_all_votes_detailed(page, per_page)
    
    items = []
    if votes:
        for v in votes:
            items.append({
                'id': v['id'],
                'user_id': v['user_id'],
                'username': v['username'],
                'comment_id': v['comment_id'],
                'vote_type': v['vote_type'],
                'comment_snippet': v['comment_snippet'],
                'created_at': v['created_at'].strftime('%Y-%m-%d %H:%M') if v['created_at'] else '-'
            })
            
    return jsonify({
        'items': items,
        'pagination': {
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page
        }
    })

@admin_bp.route('/api/votes/<int:id>', methods=['GET'])
def api_get_vote_by_id(id):
    vote, err = get_vote_by_id(id)
    if err: return jsonify({'error': err}), 404
    return jsonify(dict(vote))

@admin_bp.route('/api/votes/<int:id>', methods=['DELETE'])
def api_delete_vote(id):
    success, err = delete_vote(id)
    if err: return jsonify({'error': err}), 400
    return jsonify({'success': True}), 200