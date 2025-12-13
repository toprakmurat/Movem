from src.config.database import execute_query

def get_actors_paginated_db(page: int = 1, per_page: int = 12, search_query: str = None):
    """Get paginated list of actors with optional search"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 12
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build query based on search
        if search_query:
            # Get total count with search
            count_result = execute_query(
                "SELECT COUNT(*) as total FROM people WHERE name ILIKE %s",
                (f'%{search_query}%',),
                fetch=True
            )
            total = count_result[0]['total'] if count_result else 0
            
            # Get paginated actors with search
            actors = execute_query(
                """
                SELECT id, name, biography, birth_date, photo_url, created_at
                FROM people
                WHERE name ILIKE %s
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (f'%{search_query}%', per_page, offset),
                fetch=True
            )
        else:
            # Get total count
            count_result = execute_query(
                "SELECT COUNT(*) as total FROM people",
                fetch=True
            )
            total = count_result[0]['total'] if count_result else 0
            
            # Get paginated actors
            actors = execute_query(
                """
                SELECT id, name, biography, birth_date, photo_url, created_at
                FROM people
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (per_page, offset),
                fetch=True
            )
        
        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'actors': actors,
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


def get_actor_by_id_db(person_id: int):
    """Get a specific actor by ID"""
    try:
        actor = execute_query(
            """
            SELECT id, name, biography, birth_date, photo_url, created_at
            FROM people
            WHERE id = %s
            """,
            (person_id,),
            fetch=True
        )
        
        if not actor:
            return None, "Actor not found"
        
        return actor[0], None
        
    except Exception as e:
        return None, str(e)


def get_actor_filmography_db(person_id: int):
    """Get all movies an actor has appeared in"""
    try:
        filmography = execute_query(
            """
            SELECT DISTINCT ON (m.id)
                m.id AS movie_id,
                m.title,
                m.release_date,
                m.overview,
                m.tagline,
                m.poster_file,
                m.banner_file,
                s.vote_avg AS rating,
                s.runtime,
                mc.character_name AS role
            FROM movies m
            JOIN movie_cast mc
                ON m.id = mc.movie_id
            LEFT JOIN statistic s
                ON m.id = s.movie_id
            WHERE mc.person_id = %s
            ORDER BY
                m.id,
                m.release_date DESC;
            """,
            (person_id,),
            fetch=True
        )

        return filmography if filmography else [], None
        
    except Exception as e:
        return None, str(e)


def create_actor_db(actor_data: dict):
    """Create a new actor"""
    try:
        # Validate required fields
        if not actor_data or 'name' not in actor_data:
            return None, "Name is required"
        
        # Insert new actor
        result = execute_query(
            """
            INSERT INTO people (name, biography, birth_date, photo_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, biography, birth_date, photo_url, created_at
            """,
            (
                actor_data['name'],
                actor_data.get('biography'),
                actor_data.get('birth_date'),
                actor_data.get('photo_url')
            ),
            fetch=True
        )
        
        if result:
            return result[0], None
        return None, "Failed to create actor"
        
    except Exception as e:
        return None, str(e)


def update_actor_db(actor_id: int, actor_data: dict):
    """Update an existing actor"""
    try:
        if not actor_data:
            return None, "No data provided"
        
        # Check if actor exists
        actor = execute_query(
            "SELECT id FROM people WHERE id = %s",
            (actor_id,),
            fetch=True
        )
        
        if not actor:
            return None, "Actor not found"
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if 'name' in actor_data:
            update_fields.append("name = %s")
            params.append(actor_data['name'])
        if 'biography' in actor_data:
            update_fields.append("biography = %s")
            params.append(actor_data['biography'])
        if 'birth_date' in actor_data:
            update_fields.append("birth_date = %s")
            params.append(actor_data['birth_date'])
        if 'photo_url' in actor_data:
            update_fields.append("photo_url = %s")
            params.append(actor_data['photo_url'])
        
        if not update_fields:
            return None, "No valid fields to update"
        
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
            return result[0], None
        return None, "Failed to update actor"
        
    except Exception as e:
        return None, str(e)


def delete_actor_db(actor_id: int):
    """Delete an actor"""
    try:
        # Check if actor exists
        actor = execute_query(
            "SELECT id, name FROM people WHERE id = %s",
            (actor_id,),
            fetch=True
        )
        
        if not actor:
            return None, "Actor not found"
        
        # Delete actor
        execute_query(
            "DELETE FROM people WHERE id = %s",
            (actor_id,)
        )
        
        return actor[0], None
        
    except Exception as e:
        return None, str(e)


def get_featured_people_db(limit: int = 4):
    """Get featured people based on number of movie credits"""
    try:
        featured_people = execute_query(
            """
            SELECT
                p.id AS actor_id,
                p.name AS actor_name,

                COUNT(DISTINCT mc2.person_id) AS collaborators_count,

                COUNT(DISTINCT m.id) AS total_movies,

                ROUND(AVG(s.vote_avg), 2) AS avg_movie_rating

            FROM people p

            -- actor → their movie roles
            JOIN movie_cast mc1
                ON mc1.person_id = p.id

            -- movie they worked on
            JOIN movies m
                ON m.id = mc1.movie_id

            -- other people in the same movies
            JOIN movie_cast mc2
                ON mc2.movie_id = m.id
            AND mc2.person_id != p.id

            -- movie statistics
            LEFT JOIN statistic s
                ON s.movie_id = m.id

            GROUP BY
                p.id,
                p.name

            HAVING COUNT(DISTINCT mc2.person_id) >= 10

            ORDER BY
                collaborators_count DESC,
                total_movies DESC

            LIMIT %s;

            """,
            (limit,),
            fetch=True
        )
        
        return featured_people, None
        
    except Exception as e:
        return None, str(e)
