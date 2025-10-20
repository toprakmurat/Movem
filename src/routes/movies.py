from flask import Blueprint, jsonify, request
from src.config.database import db
from src.models.models import Movie, MovieCast, Person

movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/', methods=['GET'])
def get_movies():
    """Get all movies"""
    try:
        movies = Movie.query.all()
        return jsonify({
            'success': True,
            'data': [movie.to_dict() for movie in movies],
            'count': len(movies)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie by ID"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        
        # Get cast information
        cast_info = db.session.query(MovieCast, Person)\
            .join(Person, MovieCast.person_id == Person.id)\
            .filter(MovieCast.movie_id == movie_id)\
            .all()
        
        movie_data = movie.to_dict()
        movie_data['cast'] = [
            {
                'cast_id': cast.id,
                'role': cast.role,
                'character_name': cast.character_name,
                'actor': person.to_dict()
            }
            for cast, person in cast_info
        ]
        
        return jsonify({
            'success': True,
            'data': movie_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/', methods=['POST'])
def create_movie():
    """Create a new movie"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        movie = Movie(
            title=data['title'],
            description=data.get('description'),
            release_year=data.get('release_year'),
            type=data.get('type'),
            rating=data.get('rating', 0),
            poster_url=data.get('poster_url'),
            genre=data.get('genre'),
            platform=data.get('platform'),
            cast_id=data.get('cast_id')
        )
        
        db.session.add(movie)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': movie.to_dict(),
            'message': 'Movie created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    """Update a movie"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update fields if provided
        for field in ['title', 'description', 'release_year', 'type', 'rating', 
                     'poster_url', 'genre', 'platform', 'cast_id']:
            if field in data:
                setattr(movie, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': movie.to_dict(),
            'message': 'Movie updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """Delete a movie"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        
        # Delete associated cast entries
        MovieCast.query.filter_by(movie_id=movie_id).delete()
        
        db.session.delete(movie)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Movie deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/<int:movie_id>/cast', methods=['POST'])
def add_cast_member(movie_id):
    """Add a cast member to a movie"""
    try:
        # Verify movie exists
        Movie.query.get_or_404(movie_id)
        
        data = request.get_json()
        if not data or 'person_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Person ID is required'
            }), 400
        
        # Verify person exists
        Person.query.get_or_404(data['person_id'])
        
        cast_member = MovieCast(
            movie_id=movie_id,
            person_id=data['person_id'],
            role=data.get('role'),
            character_name=data.get('character_name')
        )
        
        db.session.add(cast_member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': cast_member.to_dict(),
            'message': 'Cast member added successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    """Search movies by title, genre, or platform"""
    try:
        query = request.args.get('q', '')
        genre = request.args.get('genre', '')
        platform = request.args.get('platform', '')
        movie_type = request.args.get('type', '')
        
        movies_query = Movie.query
        
        if query:
            movies_query = movies_query.filter(Movie.title.contains(query))
        
        if genre:
            movies_query = movies_query.filter(Movie.genre.contains(genre))
        
        if platform:
            movies_query = movies_query.filter(Movie.platform.contains(platform))
        
        if movie_type:
            movies_query = movies_query.filter(Movie.type == movie_type)
        
        movies = movies_query.all()
        
        return jsonify({
            'success': True,
            'data': [movie.to_dict() for movie in movies],
            'count': len(movies)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500