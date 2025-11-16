from flask import Blueprint, jsonify
from src.services.users_service import (
    get_users_db,
    get_user_by_id_db,
    create_user_db,
    update_user_db,
    delete_user_db,
)

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""

    users, err = get_users_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(user) for user in users]), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Get a specific user"""
    user, err = get_user_by_id_db(user_id)
    if err:
        return jsonify({"error": err}), 500
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    """Get a new movie"""
    user_data = request.get_json()
    if not user_data:
        return jsonify({"error": "No data provided"}), 400

    new_user, err = create_user_db(user_data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_user)), 201


@users_bp.route("/<int:id>", methods=["PUT"])
def update_user(id):
    """Update user by id"""
    user_data = request.get_json()
    if not user_data:
        return jsonify({"error": "No data provided"}), 400

    updated_user, err = update_user_db(id, user_data)
    if err:
        return jsonify({"error": err}), 400
    if not updated_user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(dict(updated_user)), 200



@users_bp.route("/<int:id>", methods=["DELETE"])
def delete_user(id):
    """Delete user by id"""
    deleted_user, err = delete_user_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted_user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(dict(deleted_user)), 200


