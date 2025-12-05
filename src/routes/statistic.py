from flask import Blueprint, jsonify, request
from src.services.statistic_service import (
    get_statistics_db,
    get_statistic_by_id_db,
    create_statistic_db,
    update_statistic_db,
    delete_statistic_db
)

statistic_bp = Blueprint('statistic', __name__)

@statistic_bp.route('/', methods=['GET'])
def get_statistics():
    """Get all statistics"""
    stats, err = get_statistics_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(s) for s in stats]), 200

@statistic_bp.route('/<int:movie_id>', methods=['GET'])
def get_statistic(movie_id):
    """Get statistic by movie_id"""
    stat, err = get_statistic_by_id_db(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not stat:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(stat)), 200

@statistic_bp.route('/', methods=['POST'])
def create_statistic():
    """Create a new statistic"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    new_stat, err = create_statistic_db(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_stat)), 201

@statistic_bp.route('/<int:movie_id>', methods=['PUT'])
def update_statistic(movie_id):
    """Update statistic"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    updated, err = update_statistic_db(movie_id, data)
    if err:
        return jsonify({"error": err}), 400
    if not updated:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(updated)), 200

@statistic_bp.route('/<int:movie_id>', methods=['DELETE'])
def delete_statistic(movie_id):
    """Delete statistic"""
    deleted, err = delete_statistic_db(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(deleted)), 200
