import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from src.services.users_service import create_user_db, get_user_by_email_db, update_user_db, get_user_by_id_db
from src.models.user_model import User

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

        user_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password_hash': hashed_password,
            'profile_picture': 'img/placeholder_avatar.svg'
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
        update_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'bio': request.form.get('bio')
        }

        updated_user_data, err = update_user_db(int(current_user.id), update_data)
        if not err:
            flash('Profile updated successfully!', 'success')

            return redirect(url_for('auth.account'))
        else:
            flash('Error updating profile.', 'error')

    stats = {
        'score': current_user.game_score,
        'best_streak': 0,
        'accuracy': 0,
        'games_played': 0
    }

    favorites = []
    sessions = []

    return render_template(
        'account.html',
        stats=stats,
        favorites=favorites,
        sessions=sessions
    )