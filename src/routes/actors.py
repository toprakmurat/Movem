from flask import Blueprint, jsonify
from src.config.database import execute_query

actors_bp = Blueprint('actors', __name__)


@actors_bp.route('/', methods=['GET'])
def get_actors():
    """Get all actors"""
    try:
        actors = execute_query(
            "SELECT * FROM people",
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
            "SELECT * FROM people WHERE id = %s",
            (actor_id,),
            fetch=True
        )
        if actor:
            return jsonify(dict(actor[0]))
        return jsonify({'error': 'Actor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500