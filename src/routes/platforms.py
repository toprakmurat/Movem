from flask import Blueprint, jsonify, request
from src.config.database import execute_query

platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/', methods=['GET'])
def get_all_platforms():
    """Gets all platforms"""
    try:
        platforms = execute_query(
            """
            SELECT id, platform_name, logo_path 
            FROM platforms 
            ORDER BY platform_name ASC
            """,
            fetch=True
        )
        return jsonify([dict(platform) for platform in platforms])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@platforms_bp.route('/<int:platform_id>', methods=['GET'])
def get_platform(platform_id):
    """Gets a single platform by its ID"""
    try:
        platform = execute_query(
            """
            SELECT id, platform_name, logo_path 
            FROM platforms 
            WHERE id = %s
            """,
            (platform_id,),
            fetch=True
        )
        
        if platform:
            return jsonify(dict(platform[0]))
            
        return jsonify({'error': 'Platform not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@platforms_bp.route('/', methods=['POST'])
def create_platform():
    """Creates a new platform"""
    try:
        data = request.get_json()
        
        if not data or 'platform_name' not in data:
            return jsonify({'error': 'platform_name is required'}), 400
        
        platform_name = data['platform_name']
        logo_path = data.get('logo_path', None) 
        
        new_platform = execute_query(
            """
            INSERT INTO platforms (platform_name, logo_path)
            VALUES (%s, %s)
            RETURNING *
            """,
            (platform_name, logo_path),
            fetch=True 
        )
        
        if new_platform:
            return jsonify(dict(new_platform[0])), 201
            
        return jsonify({'error': 'Failed to create platform'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@platforms_bp.route('/<int:platform_id>', methods=['PUT', 'PATCH'])
def update_platform(platform_id):
    """Updates an existing platform"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        platform_check = execute_query(
            "SELECT id FROM platforms WHERE id = %s",
            (platform_id,),
            fetch=True
        )
        
        if not platform_check:
            return jsonify({'error': 'Platform not found'}), 404
            
        update_fields = []
        params = []
        
        if 'platform_name' in data:
            update_fields.append("platform_name = %s")
            params.append(data['platform_name'])
        if 'logo_path' in data:
            update_fields.append("logo_path = %s")
            params.append(data['logo_path'])
            
        if not update_fields:
            return jsonify({'error': 'No valid fields to update (platform_name or logo_path)'}), 400
            
        params.append(platform_id) 
        
        query = f"""
            UPDATE platforms
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        
        updated_platform = execute_query(
            query,
            tuple(params),
            fetch=True
        )
        
        if updated_platform:
            return jsonify(dict(updated_platform[0]))
            
        return jsonify({'error': 'Failed to update platform'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@platforms_bp.route('/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    """Deletes a platform"""
    try:
        platform = execute_query(
            "SELECT * FROM platforms WHERE id = %s",
            (platform_id,),
            fetch=True
        )
        
        if not platform:
            return jsonify({'error': 'Platform not found'}), 404
            
        execute_query(
            "DELETE FROM platforms WHERE id = %s",
            (platform_id,)
        )
        
        return jsonify({
            'message': 'Platform deleted successfully',
            'platform': dict(platform[0])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500