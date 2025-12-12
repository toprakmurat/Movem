from flask import Blueprint, jsonify, request, render_template
from src.services.actors_service import (
    get_actors_paginated_db,
    get_actor_by_id_db,
    get_actor_filmography_db,
    create_actor_db,
    update_actor_db,
    delete_actor_db
)

actors_bp = Blueprint('actors', __name__) 

# Column names are written explicitly on purpose in SELECT statements.
# This makes debugging easier in case the database table changes.

@actors_bp.route('/', methods=['GET'])
def get_actors():
    """Get all actors with pagination - serves HTML or JSON based on request"""
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search_query = request.args.get('q', '').strip() if request.args.get('q') else None
    
    # Get paginated actors from service
    result, error = get_actors_paginated_db(page, per_page, search_query)
    
    if error:
        return jsonify({'error': error}), 500
    
    actors = result['actors']
    pagination = result['pagination']
    
    # Check if request wants JSON (AJAX request) or HTML (browser request)
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        # Return JSON for API calls
        return jsonify({
            'actors': [dict(actor) for actor in actors],
            'pagination': pagination
        })
    else:
        # Render HTML template for browser requests
        return render_template('people.html', 
                                actors=[dict(actor) for actor in actors],
                                pagination=pagination)

@actors_bp.route('/<int:person_id>', methods=['GET'])
def person_detail(person_id):
    """Get a specific actor - serves HTML or JSON based on request"""
    # Get actor details
    actor, error = get_actor_by_id_db(person_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Get actor's filmography
    filmography, error = get_actor_filmography_db(person_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    # Check if request wants JSON or HTML
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        return jsonify({
            'actor': dict(actor),
            'filmography': [dict(film) for film in filmography]
        })
    else:
        return render_template(
            'person_detail.html', 
            person=dict(actor),
            filmography=[dict(film) for film in filmography]
        )


@actors_bp.route('/<int:actor_id>/movies', methods=['GET'])
def get_actor_movies(actor_id):
    """Get all movies for an actor"""
    # Check if actor exists
    actor, error = get_actor_by_id_db(actor_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Get actor's filmography
    filmography, error = get_actor_filmography_db(actor_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'actor': dict(actor),
        'filmography': [dict(film) for film in filmography],
        'total_movies': len(filmography)
    })


@actors_bp.route('/', methods=['POST'])
def create_actor():
    """Create a new actor"""
    data = request.get_json()
    
    # Create actor using service
    result, error = create_actor_db(data)
    
    if error:
        status_code = 400 if error == 'Name is required' else 500
        return jsonify({'error': error}), status_code
    
    return jsonify(dict(result)), 201

# TODO: Subject to change, might better handle parameters with a helper function
@actors_bp.route('/<int:actor_id>', methods=['PUT'])
def update_actor(actor_id):
    """Update an existing actor"""
    data = request.get_json()
    
    # Update actor using service
    result, error = update_actor_db(actor_id, data)
    
    if error:
        if error == 'Actor not found':
            return jsonify({'error': error}), 404
        elif error in ['No data provided', 'No valid fields to update']:
            return jsonify({'error': error}), 400
        return jsonify({'error': error}), 500
    
    return jsonify(dict(result))


@actors_bp.route('/<int:actor_id>', methods=['DELETE'])
def delete_actor(actor_id):
    """Delete an actor"""
    # Delete actor using service
    result, error = delete_actor_db(actor_id)
    
    if error:
        status_code = 404 if error == 'Actor not found' else 500
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'message': 'Actor deleted successfully',
        'actor': dict(result)
    })
