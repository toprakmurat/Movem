from flask import Blueprint, jsonify, request, render_template
from src.config.database import db
from src.models.models import Person, MovieCast, Movie

actors_bp = Blueprint('actors', __name__)


@actors_bp.route('/', methods=['GET'])
def get_actors():
    """Get all actors/people"""
    try:
        actors = Person.query.all()
        return render_template('actors.html', actors=actors)
    except Exception as e:
        # In case of error, still render the template with empty actors list
        return render_template('actors.html', actors=[])


@actors_bp.route('/<int:actor_id>', methods=['GET'])
def get_actor(actor_id):
    """Get a specific actor by ID"""
    try:
        actor = Person.query.get_or_404(actor_id)
        
        # Get movies this actor has been in
        movie_roles = db.session.query(MovieCast, Movie)\
            .join(Movie, MovieCast.movie_id == Movie.id)\
            .filter(MovieCast.person_id == actor_id)\
            .all()
        
        actor_data = actor.to_dict()
        actor_data['movies'] = [
            {
                'cast_id': cast.id,
                'role': cast.role,
                'character_name': cast.character_name,
                'movie': movie.to_dict()
            }
            for cast, movie in movie_roles
        ]
        
        return jsonify({
            'success': True,
            'data': actor_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@actors_bp.route('/', methods=['POST'])
def create_actor():
    """Create a new actor/person"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        # Parse birth_date if provided
        birth_date = None
        if 'birth_date' in data and data['birth_date']:
            from datetime import datetime
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Birth date must be in YYYY-MM-DD format'
                }), 400
        
        actor = Person(
            name=data['name'],
            biography=data.get('biography'),
            birth_date=birth_date,
            photo_url=data.get('photo_url')
        )
        
        db.session.add(actor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': actor.to_dict(),
            'message': 'Actor created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@actors_bp.route('/<int:actor_id>', methods=['PUT'])
def update_actor(actor_id):
    """Update an actor"""
    try:
        actor = Person.query.get_or_404(actor_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update fields if provided
        if 'name' in data:
            actor.name = data['name']
        if 'biography' in data:
            actor.biography = data['biography']
        if 'photo_url' in data:
            actor.photo_url = data['photo_url']
        
        # Handle birth_date update
        if 'birth_date' in data:
            if data['birth_date']:
                from datetime import datetime
                try:
                    actor.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Birth date must be in YYYY-MM-DD format'
                    }), 400
            else:
                actor.birth_date = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': actor.to_dict(),
            'message': 'Actor updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@actors_bp.route('/<int:actor_id>', methods=['DELETE'])
def delete_actor(actor_id):
    """Delete an actor"""
    try:
        actor = Person.query.get_or_404(actor_id)
        
        # Delete associated cast entries
        MovieCast.query.filter_by(person_id=actor_id).delete()
        
        db.session.delete(actor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Actor deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@actors_bp.route('/search', methods=['GET'])
def search_actors():
    """Search actors by name"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        actors = Person.query.filter(Person.name.contains(query)).all()
        
        return jsonify({
            'success': True,
            'data': [actor.to_dict() for actor in actors],
            'count': len(actors)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500