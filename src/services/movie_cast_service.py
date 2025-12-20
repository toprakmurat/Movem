from src.config.database import execute_query

def get_movie_cast_paginated_db(page: int = 1, per_page: int = 12):
    """Get paginated list of movie cast entries"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 12
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        count_result = execute_query(
            "SELECT COUNT(*) as total FROM movie_cast",
            fetch=True
        )
        total = count_result[0]['total'] if count_result else 0
        
        # Get paginated movie cast entries
        cast_entries = execute_query(
            """
            SELECT 
                mc.movie_id,
                mc.person_id,
                mc.role,
                mc.character_name,
                m.title AS movie_title,
                p.name AS person_name
            FROM movie_cast mc
            JOIN movies m ON mc.movie_id = m.id
            JOIN people p ON mc.person_id = p.id
            ORDER BY mc.movie_id, mc.person_id
            LIMIT %s OFFSET %s
            """,
            (per_page, offset),
            fetch=True
        )
        
        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'cast_entries': cast_entries,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }, None
        
    except Exception as e:
        return None, str(e)

def get_movie_cast_by_composite_key_db(movie_id: int, person_id: int, character_name: str):
    """Get a specific movie cast entry by composite key"""
    try:
        cast_entry = execute_query(
            """
            SELECT 
                mc.movie_id,
                mc.person_id,
                mc.role,
                mc.character_name,
                m.title AS movie_title,
                p.name AS person_name
            FROM movie_cast mc
            JOIN movies m ON mc.movie_id = m.id
            JOIN people p ON mc.person_id = p.id
            WHERE mc.movie_id = %s AND mc.person_id = %s AND mc.character_name = %s
            """,
            (movie_id, person_id, character_name),
            fetch=True
        )
        
        if not cast_entry:
            return None, "Movie cast entry not found"
        
        return cast_entry[0], None
        
    except Exception as e:
        return None, str(e)


def get_cast_by_movie_db(movie_id: int):
    """Get all cast entries for a specific movie"""
    try:
        cast_entries = execute_query(
            """
            SELECT 
                p.id,
                p.name,
                p.birth_date,
                p.biography,
                p.photo_url,
                mc.role,
                mc.character_name
            FROM movie_cast mc
            JOIN people p ON mc.person_id = p.id
            WHERE mc.movie_id = %s
            ORDER BY 
                CASE WHEN mc.role = 'Director' THEN 0 ELSE 1 END,
                p.name
            """,
            (movie_id,),
            fetch=True
        )
        
        return cast_entries if cast_entries else [], None
        
    except Exception as e:
        return None, str(e)


def get_cast_by_person_db(person_id: int):
    """Get all cast entries for a specific person"""
    try:
        cast_entries = execute_query(
            """
            SELECT 
                mc.movie_id,
                mc.person_id,
                mc.role,
                mc.character_name,
                m.title AS movie_title,
                m.poster_file AS movie_poster
            FROM movie_cast mc
            JOIN movies m ON mc.movie_id = m.id
            WHERE mc.person_id = %s
            ORDER BY m.title
            """,
            (person_id,),
            fetch=True
        )
        
        return cast_entries if cast_entries else [], None
        
    except Exception as e:
        return None, str(e)


def create_movie_cast_db(cast_data: dict):
    """Create a new movie cast entry"""
    try:
        # Validate required fields
        if not cast_data or 'movie_id' not in cast_data or 'person_id' not in cast_data:
            return None, "movie_id and person_id are required"
        
        # Insert new movie cast entry
        # character_name defaults to 'Unknown' in the database if not provided
        character_name = cast_data.get('character_name', 'Unknown')
        result = execute_query(
            """
            INSERT INTO movie_cast (movie_id, person_id, role, character_name)
            VALUES (%s, %s, %s, %s)
            RETURNING movie_id, person_id, role, character_name
            """,
            (
                cast_data['movie_id'],
                cast_data['person_id'],
                cast_data.get('role'),
                character_name
            ),
            fetch=True
        )
        
        if result:
            return result[0], None
        return None, "Failed to create movie cast entry"
        
    except Exception as e:
        return None, str(e)


def update_movie_cast_db(movie_id: int, person_id: int, character_name: str, cast_data: dict):
    """Update an existing movie cast entry identified by composite key"""
    try:
        if not cast_data:
            return None, "No data provided"
        
        # Check if cast entry exists
        cast_entry = execute_query(
            "SELECT movie_id FROM movie_cast WHERE movie_id = %s AND person_id = %s AND character_name = %s",
            (movie_id, person_id, character_name),
            fetch=True
        )
        
        if not cast_entry:
            return None, "Movie cast entry not found"
        
        # Build update query dynamically based on provided fields
        # Note: Updating primary key fields requires DELETE + INSERT
        update_fields = []
        params = []
        
        if 'role' in cast_data:
            update_fields.append("role = %s")
            params.append(cast_data['role'])
        
        if not update_fields:
            return None, "No valid fields to update (movie_id, person_id, and character_name are part of primary key and cannot be updated directly)"
        
        params.extend([movie_id, person_id, character_name])
        
        # Update movie cast entry
        result = execute_query(
            f"""
            UPDATE movie_cast
            SET {', '.join(update_fields)}
            WHERE movie_id = %s AND person_id = %s AND character_name = %s
            RETURNING movie_id, person_id, role, character_name
            """,
            tuple(params),
            fetch=True
        )
        
        if result:
            return result[0], None
        return None, "Failed to update movie cast entry"
        
    except Exception as e:
        return None, str(e)


def delete_movie_cast_db(movie_id: int, person_id: int, character_name: str):
    """Delete a movie cast entry identified by composite key"""
    try:
        # Check if cast entry exists
        cast_entry = execute_query(
            "SELECT movie_id, person_id, character_name FROM movie_cast WHERE movie_id = %s AND person_id = %s AND character_name = %s",
            (movie_id, person_id, character_name),
            fetch=True
        )
        
        if not cast_entry:
            return None, "Movie cast entry not found"
        
        # Delete cast entry
        execute_query(
            "DELETE FROM movie_cast WHERE movie_id = %s AND person_id = %s AND character_name = %s",
            (movie_id, person_id, character_name)
        )
        
        return cast_entry[0], None
        
    except Exception as e:
        return None, str(e)
