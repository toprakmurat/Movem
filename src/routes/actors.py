from flask import Blueprint, jsonify, request
from src.config.database import execute_query

actors_bp = Blueprint('actors', __name__)

# Column names are written explicitly on purpose in SELECT statements.
# This makes debugging easier in case the database table changes.

@actors_bp.route('/', methods=['GET'])
def get_actors():
    """Get all actors"""
    try:
        actors = execute_query(
            """
            SELECT id, name, biography, birth_date, photo_url, created_at
            FROM people
            ORDER BY name
            """,
            fetch=True
        )
        
        return jsonify([dict(actor) for actor in actors])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@actors_bp.route('/<int:actor_id>', methods=['GET'])
def get_actor(actor_id):
    """Get a specific actor"""
    try:
        actor = execute_query(
            """
            SELECT id, name, biography, birth_date, photo_url, created_at
            FROM people
            WHERE id = %s
            """,
            (actor_id,),
            fetch=True
        )
        if actor:
            return jsonify(dict(actor[0]))
        return jsonify({'error': 'Actor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@actors_bp.route('/', methods=['POST'])
def create_actor():
    """Create a new actor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        # Insert new actor
        result = execute_query(
            """
            INSERT INTO people (name, biography, birth_date, photo_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, biography, birth_date, photo_url, created_at
            """,
            (
                data['name'],
                data.get('biography'),
                data.get('birth_date'),
                data.get('photo_url')
            ),
            fetch=True
            # RETURNING makes the query produce rows, just like a SELECT query. No need to have a separate query.
            # Therefore, fetch must be equal to True to get the newly inserted row
        )
        
        if result:
            return jsonify(dict(result[0])), 201
        return jsonify({'error': 'Failed to create actor'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# TODO: Subject to change, might better handle parameters with a helper function
@actors_bp.route('/<int:actor_id>', methods=['PUT'])
def update_actor(actor_id):
    """Update an existing actor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if actor exists
        actor = execute_query(
            "SELECT id FROM people WHERE id = %s",
            (actor_id,),
            fetch=True
        )
        
        if not actor:
            return jsonify({'error': 'Actor not found'}), 404
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        if 'biography' in data:
            update_fields.append("biography = %s")
            params.append(data['biography'])
        if 'birth_date' in data:
            update_fields.append("birth_date = %s")
            params.append(data['birth_date'])
        if 'photo_url' in data:
            update_fields.append("photo_url = %s")
            params.append(data['photo_url'])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(actor_id)
        
        # Update actor
        result = execute_query(
            f"""
            UPDATE people
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, biography, birth_date, photo_url, created_at
            """,
            tuple(params),
            fetch=True
        )
        
        if result:
            return jsonify(dict(result[0]))
        return jsonify({'error': 'Failed to update actor'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@actors_bp.route('/<int:actor_id>', methods=['DELETE'])
def delete_actor(actor_id):
    """Delete an actor"""
    try:
        # Check if actor exists
        actor = execute_query(
            "SELECT id, name FROM people WHERE id = %s",
            (actor_id,),
            fetch=True
        )
        
        if not actor:
            return jsonify({'error': 'Actor not found'}), 404
        
        # Delete actor
        execute_query(
            "DELETE FROM people WHERE id = %s",
            (actor_id,)
            # Remember, ON DELETE CASCADE in movie_cast table
        )
        
        return jsonify({
            'message': 'Actor deleted successfully',
            'actor': dict(actor[0])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500