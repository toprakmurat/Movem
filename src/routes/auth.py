import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from src.services.favorite_service import get_favorite_movies_detailed_for_user_db
from src.utils.pagination_utils import Pagination
from datetime import datetime, timedelta
import secrets
import math

from src.services.users_service import (
    create_user_db, 
    get_user_by_email_db, 
    update_user_db, 
    get_user_by_id_db, 
    update_password_db,
    set_reset_token_db,
    get_user_by_reset_token_db,
    clear_reset_token_db,
    delete_user_db,
    get_user_favorite_genre_stats_db,
    get_user_favorite_actor_stats_db
)
from src.services.list_service import create_custom_list_db, get_lists_by_user_db
from src.models.user_model import User
from src.services.comments_service import get_comments_by_user
from src.utils.file_utils import save_profile_picture

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user_data, error = get_user_by_email_db(email)


        if user_data and check_password_hash(user_data['password_hash'], password):
            user_obj = User(user_data)
            login_user(user_obj, remember=remember)
            return redirect(url_for('auth.account'))
        else:
            flash('Please check your login details and try again.', 'error')

    return render_template('auth/login.html', form=None)



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')


        user_check, _ = get_user_by_email_db(email)
        if user_check:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))


        hashed_password = generate_password_hash(password)

        profile_pic_path = 'img/placeholder_avatar.svg'
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                profile_pic_path = save_profile_picture(file)

        user_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password_hash': hashed_password,
            'profile_picture': profile_pic_path
        }

        new_user, error = create_user_db(user_data)
        if error:
            flash(f"Error: {error}", 'error')
        else:

            user_obj = User(new_user)
            login_user(user_obj)
            return redirect(url_for('auth.account'))

    return render_template('auth/register.html', form=None)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():

    if request.method == 'POST':
        # Handle List Creation
        if 'create_list' in request.form:
            list_name = request.form.get('list_name')
            is_public = True if request.form.get('is_public') else False
            if list_name:
                _, err = create_custom_list_db(int(current_user.id), list_name, is_public)
                if err:
                    flash(f'Error creating list: {err}', 'error')
                else:
                    flash(f'List "{list_name}" created successfully!', 'success')
                    return redirect(url_for('auth.account'))
        
        # Handle Profile Update
        else:
            update_data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'bio': request.form.get('bio')
            }

            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '':
                    picture_file = save_profile_picture(file)
                    update_data['profile_picture'] = picture_file

            updated_user_data, err = update_user_db(int(current_user.id), update_data)
            if not err:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('auth.account'))
            else:
                flash('Error updating profile.', 'error')

    stats = {
        'score': current_user.game_score
    }

    # Fetch User Stats
    genre_stats, _ = get_user_favorite_genre_stats_db(current_user.id)
    actor_stats = get_user_favorite_actor_stats_db(current_user.id)
    
    # Fetch User Lists
    user_lists, _ = get_lists_by_user_db(current_user.id)
    if not user_lists: user_lists = []

    user_reviews, err = get_comments_by_user(current_user.id)
    if not user_reviews:
        user_reviews = []

    favorites, fav_err = get_favorite_movies_detailed_for_user_db(int(current_user.id))
    if not favorites or fav_err:
        favorites = []
    sessions = []

    return render_template(
        'account.html',
        stats=stats,
        favorites=favorites,
        sessions=sessions,
        user_reviews=user_reviews,
        genre_stats=genre_stats,
        actor_stats=actor_stats,
        user_lists=user_lists
    )


@auth_bp.route('/user/<int:user_id>')
def public_profile(user_id):
    target_user, err = get_user_by_id_db(user_id)

    if not target_user:
        return render_template("404.html"), 404

    user_reviews, _ = get_comments_by_user(user_id)
    if not user_reviews:
        user_reviews = []

    stats = {
        'score': target_user.get('game_score', 0)
    }

    genre_stats, _ = get_user_favorite_genre_stats_db(user_id)
    actor_stats = get_user_favorite_actor_stats_db(user_id)
    user_lists, _ = get_lists_by_user_db(user_id)
    if not user_lists: user_lists = []

    favorites, _ = get_favorite_movies_detailed_for_user_db(user_id)
    if not favorites:
        favorites = []

    return render_template(
        'account.html', 
        user=target_user,
        user_reviews=user_reviews, 
        stats=stats, 
        is_public=True,
        favorites=favorites,
        genre_stats=genre_stats,
        actor_stats=actor_stats,
        user_lists=user_lists
    )

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Verify current password
    user_data, _ = get_user_by_id_db(int(current_user.id))
    if not user_data or not check_password_hash(user_data['password_hash'], current_password):
        flash('Incorrect current password.', 'error')
        return redirect(url_for('auth.account'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.account'))

    new_hash = generate_password_hash(new_password)
    success, err = update_password_db(int(current_user.id), new_hash)

    if success:
        flash('Password changed successfully.', 'success')
    else:
        flash('Error changing password.', 'error')
    
    return redirect(url_for('auth.account'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))

    if request.method == 'POST':
        email = request.form.get('email')
        user, err = get_user_by_email_db(email)
        
        if user:
            # Generate token
            token = secrets.token_urlsafe(32)
            # Expiry in 1 hour
            expiry = datetime.now() + timedelta(hours=1)
            

            success, err = set_reset_token_db(email, token, expiry)

            if success:
                # In a real app, send email here. For this task, print to console.
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                print(f"\n{'='*50}\nPASSWORD RESET LINK: {reset_url}\n{'='*50}\n", flush=True)
                flash('If an account exists with that email, a reset link has been sent (check server console).', 'success')
            else:
                flash('Error generating reset token.', 'error')
        else:
            print(f"\n[DEBUG] Password reset requested for {email}, but no user found.\n", flush=True)
            # Don't reveal if user exists or not, but for this simple app maybe we don't care about timing attacks
            flash('If an account exists with that email, a reset link has been sent (check server console).', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))
        
    user, err = get_user_by_reset_token_db(token)
    
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token) # Keep on page?
            
        hashed_password = generate_password_hash(password)
        success, err = update_password_db(user['id'], hashed_password)
        
        if success:
            clear_reset_token_db(user['id'])
            flash('Password reset successfully. You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error resetting password.', 'error')

    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Double check it is the current user
    user_id = int(current_user.id)
    deleted_user, err = delete_user_db(user_id)
    
    if deleted_user:
        logout_user()
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(f'Error deleting account: {err}', 'error')
        return redirect(url_for('auth.account'))

@auth_bp.route('/account/favorites', methods=['GET'])
@login_required
def favorites_page():
    """
    Return favorites for user
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10  

    all_favorites, err = get_favorite_movies_detailed_for_user_db(int(current_user.id))
    
    if err or not all_favorites:
        all_favorites = []

    total_items = len(all_favorites)
    
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    current_page_favorites = all_favorites[start:end]

    pagination = Pagination(
        items=current_page_favorites,
        page=page,
        per_page=per_page,
        total_count=total_items
    )

    return render_template(
        'favorites.html',  
        favorites=current_page_favorites,
        pagination=pagination
    )

@auth_bp.route('/user/<int:user_id>/reviews')
def user_reviews_page(user_id):
    """
    Displays all reviews for a specific user with pagination.
    """
    target_user, err = get_user_by_id_db(user_id)
    if not target_user:
        return render_template("404.html"), 404

    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    all_reviews, err = get_comments_by_user(user_id)
    if not all_reviews:
        all_reviews = []
        
    total_items = len(all_reviews)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    current_page_reviews = all_reviews[start:end]
    
    pagination = Pagination(
        items=current_page_reviews,
        page=page,
        per_page=per_page,
        total_count=total_items
    )

    return render_template(
        'user_reviews.html',
        user=target_user,
        reviews=current_page_reviews,
        pagination=pagination
    )