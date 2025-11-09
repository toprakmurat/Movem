from flask import Blueprint, jsonify
from src.config.database import execute_query

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = execute_query(
            "SELECT * FROM users",
            fetch=True
        )
        return jsonify([dict(user) for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    try:
        user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch=True
        )
        if user:
            return jsonify(dict(user[0]))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500