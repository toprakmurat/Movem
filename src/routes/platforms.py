from flask import Blueprint, jsonify, request
from src.services.platforms_service import (
    get_platforms,
    get_platform_by_id,
    create_platform,
    update_platform,
    delete_platform_by_id
)

platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/', methods=['GET'])
def get_all_platforms_route():
    """Gets all platforms"""
    platforms, err = get_platforms()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(p) for p in platforms]), 200


@platforms_bp.route('/<int:platform_id>', methods=['GET'])
def get_platform_route(platform_id):
    """Gets a single platform by its ID"""
    platform, err = get_platform_by_id(platform_id)
    if err:
        if err == "Platform not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
    return jsonify(dict(platform)), 200


@platforms_bp.route('/', methods=['POST'])
def create_platform_route():
    """Creates a new platform"""
    data = request.get_json()
    if not data or 'platform_name' not in data:
        return jsonify({'error': 'platform_name is required'}), 400
        
    new_platform, err = create_platform(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_platform)), 201


@platforms_bp.route('/<int:platform_id>', methods=['PUT', 'PATCH'])
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


@platforms_bp.route('/<int:platform_id>', methods=['DELETE'])
def delete_platform_route(platform_id):
    """Deletes a platform"""
    deleted, err = delete_platform_by_id(platform_id)
    
    if err:
        if err == "Platform not found":
            return jsonify({"message": err}), 404
        return jsonify({"error": err}), 500
        
    return jsonify(dict(deleted)), 200