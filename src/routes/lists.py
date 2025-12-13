from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from src.services.list_service import (
    add_movie_to_list_db,
    remove_movie_from_list_db,
    get_list_details_db,
    delete_list_db
)

lists_bp = Blueprint('lists', __name__, url_prefix='/lists')

@lists_bp.route('/<int:list_id>')
def view_list(list_id):
    list_data, err = get_list_details_db(list_id)
    if not list_data:
        flash('List not found.', 'error')
        return redirect(url_for('home.home'))
        
    is_owner = False
    if current_user.is_authenticated and int(current_user.id) == list_data['list_info']['user_id']:
        is_owner = True
        
    if not list_data['list_info']['is_public'] and not is_owner:
         flash('This list is private.', 'error')
         return redirect(url_for('home.home'))

    return render_template(
        'lists/view.html',
        list_info=list_data['list_info'],
        movies=list_data['movies'],
        is_owner=is_owner
    )

@lists_bp.route('/add', methods=['POST'])
@login_required
def add_to_list():
    try:
        list_id = int(request.form.get('list_id'))
        movie_id = int(request.form.get('movie_id'))
    except (ValueError, TypeError):
        flash('Invalid request parameters.', 'error')
        return redirect(url_for('home.home'))
    
    # Verify ownership
    list_details, _ = get_list_details_db(list_id)

    if not list_details or list_details['list_info']['user_id'] != int(current_user.id):
        flash('Permission denied.', 'error')
        return redirect(url_for('home.home'))

    _, err = add_movie_to_list_db(list_id, movie_id)
    if err:
        flash(f'Error adding movie: {err}', 'error')
    else:
        flash('Movie added to list.', 'success')
        
    return redirect(url_for('movies.movies_details_page', movie_id=movie_id))

@lists_bp.route('/remove', methods=['POST'])
@login_required
def remove_from_list():
    try:
        list_id = int(request.form.get('list_id'))
        movie_id = int(request.form.get('movie_id'))
    except (ValueError, TypeError):
         flash('Invalid request parameters.', 'error')
         return redirect(url_for('home.home'))
    
    # Verify ownership
    list_details, _ = get_list_details_db(list_id)
    if not list_details or list_details['list_info']['user_id'] != int(current_user.id):
         flash('Permission denied.', 'error')
         return redirect(url_for('home.home'))
         
    _, err = remove_movie_from_list_db(list_id, movie_id)
    if err:
        flash(f'Error removing movie: {err}', 'error')
    else:
        flash('Movie removed from list.', 'success')
        
    return redirect(url_for('lists.view_list', list_id=list_id))

@lists_bp.route('/delete/<int:list_id>', methods=['POST'])
@login_required
def delete_list(list_id):
    # delete_list_db checks ownership internally by accepting user_id, 
    # but let's be explicit and pass current_user.id
    _, err = delete_list_db(list_id, int(current_user.id))
    
    if err:
        flash(f'Error deleting list: {err}', 'error')
    else:
        flash('List deleted successfully.', 'success')
        
    return redirect(url_for('auth.account'))
