from flask import Blueprint, render_template, request, jsonify
from src.services.nexus_service import (
    get_random_movie_id,
    get_nexus_data,
    get_shared_movies_by_people,
    search_movies
)

nexus_bp = Blueprint('nexus', __name__)


@nexus_bp.route('/', methods=['GET'])
def nexus():
    """Render the Nexus visualization page for a movie's cast and crew connections"""
    
    # Get movie_id from query params or random flag
    movie_id = request.args.get('movie_id', type=int)
    random_movie = request.args.get('random', type=int)
    
    # Use random movie if requested or no movie_id provided
    if not movie_id or random_movie:
        movie_id = get_random_movie_id()
    
    # Get all nexus data for the selected movie
    nexus_data = get_nexus_data(movie_id) if movie_id else None
    
    # Check if request wants JSON or HTML
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        if not nexus_data:
            return jsonify({
                'movie': None,
                'director': None,
                'actors': [],
                'related_movies': []
            })
        
        return jsonify({
            'movie': nexus_data['movie'],
            'director': nexus_data['director'],
            'actors': nexus_data['actors'],
            'related_movies': nexus_data['related_movies']
        })
    else:
        # Handle case where movie not found
        if not nexus_data:
            return render_template('nexus.html',
                                 movie=None,
                                 director=None,
                                 actors=[],
                                 related_movies=[])
        
        return render_template('nexus.html',
                              movie=nexus_data['movie'],
                              director=nexus_data['director'],
                              actors=nexus_data['actors'],
                              related_movies=nexus_data['related_movies'])

@nexus_bp.route('/shared', methods=['POST'])
def get_shared_content():
    """API Endpoint to get movies shared by specific people"""
    data = request.get_json()
    person_ids = data.get('person_ids', [])
    
    if not person_ids:
        return jsonify({'movies': []})
        
    movies = get_shared_movies_by_people(person_ids)
    return jsonify({'movies': movies})

@nexus_bp.route('/search', methods=['GET'])
def search():
    """API Endpoint for live movie search"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'results': []})
        
    results = search_movies(query, limit=3)
    return jsonify({'results': results})
