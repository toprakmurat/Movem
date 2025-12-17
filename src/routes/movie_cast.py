from flask import Blueprint, jsonify, request, render_template
from src.utils.decorators import admin_required
from src.services.movie_cast_service import (
    get_movie_cast_paginated_db,
    get_movie_cast_by_id_db,
    get_cast_by_movie_db,
    get_cast_by_person_db,
    create_movie_cast_db,
    update_movie_cast_db,
    delete_movie_cast_db
)

movie_cast_bp = Blueprint('movie_cast', __name__)

# Column names are written explicitly on purpose in SELECT statements.
# This makes debugging easier in case the database table changes.

@movie_cast_bp.route('/page/<int:movie_id>', methods=['GET'])
def movie_cast_page(movie_id):
    """Get all people (cast members) and render the movie_cast.html template"""
    people, error = get_cast_by_movie_db(movie_id)
    
    if error:
        return render_template('movie_cast.html', people=[], error=error)
    
    # Convert to list of dicts for template
    people_list = [dict(person) for person in people]
    
    return render_template('movie_cast.html', people=people_list)

@movie_cast_bp.route('/', methods=['GET'])
def get_movie_cast():
    """Get all movie cast entries with pagination - returns JSON only"""
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Get paginated movie cast entries from service
    result, error = get_movie_cast_paginated_db(page, per_page)
    
    if error:
        return jsonify({'error': error}), 500
    
    cast_entries = result['cast_entries']
    pagination = result['pagination']
    
    return jsonify({
        'cast_entries': [dict(entry) for entry in cast_entries],
        'pagination': pagination
    })

# USAGE IS NOT RECOMMENDED AS MOVIE CAST ID IS A SERIAL PRIMARY KEY
@movie_cast_bp.route('/<int:cast_id>', methods=['GET'])
def get_movie_cast_by_id(cast_id):
    """Get a specific movie cast entry by ID - returns JSON only"""
    # Get cast entry details
    cast_entry, error = get_movie_cast_by_id_db(cast_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({
        'cast_entry': cast_entry
    })


@movie_cast_bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_cast_by_movie(movie_id):
    """Get all cast entries for a specific movie - returns JSON only"""
    cast_entries, error = get_cast_by_movie_db(movie_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'movie_id': movie_id,
        'cast_entries': [dict(entry) for entry in cast_entries],
        'total_cast': len(cast_entries)
    })


@movie_cast_bp.route('/person/<int:person_id>', methods=['GET'])
def get_cast_by_person(person_id):
    """Get all cast entries for a specific person - returns JSON only"""
    cast_entries, error = get_cast_by_person_db(person_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'person_id': person_id,
        'cast_entries': [dict(entry) for entry in cast_entries],
        'total_roles': len(cast_entries)
    })


@movie_cast_bp.route('/', methods=['POST'])
@admin_required
def create_movie_cast():
    """Create a new movie cast entry - returns JSON only"""
    data = request.get_json()
    
    # Create movie cast entry using service
    result, error = create_movie_cast_db(data)
    
    if error:
        status_code = 400 if error == 'movie_id and person_id are required' else 500
        return jsonify({'error': error}), status_code
    
    return jsonify(dict(result)), 201


@movie_cast_bp.route('/<int:cast_id>', methods=['PUT'])
@admin_required
def update_movie_cast(cast_id):
    """Update an existing movie cast entry - returns JSON only"""
    data = request.get_json()
    
    # Update movie cast entry using service
    result, error = update_movie_cast_db(cast_id, data)
    
    if error:
        if error == 'Movie cast entry not found':
            return jsonify({'error': error}), 404
        elif error in ['No data provided', 'No valid fields to update']:
            return jsonify({'error': error}), 400
        return jsonify({'error': error}), 500
    
    return jsonify(dict(result))


@movie_cast_bp.route('/<int:cast_id>', methods=['DELETE'])
@admin_required
def delete_movie_cast(cast_id):
    """Delete a movie cast entry - returns JSON only"""
    # Delete movie cast entry using service
    result, error = delete_movie_cast_db(cast_id)
    
    if error:
        status_code = 404 if error == 'Movie cast entry not found' else 500
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'message': 'Movie cast entry deleted successfully',
        'cast_entry': dict(result)
    })
