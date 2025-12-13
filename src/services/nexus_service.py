from src.config.database import execute_query


def get_random_movie_id():
    """Get a random movie ID from the database"""
    result = execute_query(
        "SELECT id FROM movies ORDER BY RANDOM() LIMIT 1",
        fetch=True
    )
    return result[0]['id'] if result else None


def get_movie_with_details(movie_id):
    """Get movie details including rating and genres"""
    movie_result = execute_query(
        """
        SELECT 
            m.id,
            m.title,
            m.overview,
            m.tagline,
            m.release_date,
            m.poster_file as poster_url,
            m.banner_file,
            EXTRACT(YEAR FROM m.release_date) as year,
            s.vote_avg as rating
        FROM movies m
        LEFT JOIN statistic s ON m.id = s.movie_id
        WHERE m.id = %s
        """,
        (movie_id,),
        fetch=True
    )
    
    if not movie_result:
        return None
    
    movie = dict(movie_result[0])
    
    # Get genres
    genres_result = execute_query(
        """
        SELECT g.genre_name
        FROM genres g
        JOIN movies_genres mg ON g.id = mg.genre_id
        WHERE mg.movie_id = %s
        """,
        (movie_id,),
        fetch=True
    )
    movie['genre_list'] = [g['genre_name'] for g in genres_result] if genres_result else []
    
    return movie


def get_movie_director(movie_id):
    """Get the director of a movie"""
    result = execute_query(
        """
        SELECT DISTINCT
            p.id,
            p.name,
            p.photo_url as profile_url,
            (
                SELECT COUNT(DISTINCT mc2.movie_id)
                FROM movie_cast mc2
                WHERE mc2.person_id = p.id
            ) as collaborations
        FROM people p
        JOIN movie_cast mc ON p.id = mc.person_id
        WHERE mc.movie_id = %s AND LOWER(mc.role) = 'director'
        LIMIT 1
        """,
        (movie_id,),
        fetch=True
    )
    return dict(result[0]) if result else None


def get_movie_actors(movie_id, limit=6):
    """Get top actors from a movie (excluding director)"""
    result = execute_query(
        """
        SELECT 
            p.id,
            p.name,
            p.photo_url as profile_url,
            mc.character_name as character,
            (
                SELECT COUNT(DISTINCT mc2.movie_id)
                FROM movie_cast mc2
                WHERE mc2.person_id = p.id
            ) as collaborations
        FROM people p
        JOIN movie_cast mc ON p.id = mc.person_id
        WHERE mc.movie_id = %s AND LOWER(mc.role) != 'director'
        ORDER BY mc.id
        LIMIT %s
        """,
        (movie_id, limit),
        fetch=True
    )
    return [dict(actor) for actor in result] if result else []


def get_related_movies(movie_id, min_shared_people=2, limit=4):
    """Get movies with shared cast/crew members"""
    # Get all people involved in this movie
    people_result = execute_query(
        """
        SELECT DISTINCT person_id
        FROM movie_cast
        WHERE movie_id = %s
        """,
        (movie_id,),
        fetch=True
    )
    
    person_ids = [p['person_id'] for p in people_result] if people_result else []
    
    if not person_ids:
        return []
    
    # Find other movies with shared people
    result = execute_query(
        """
        SELECT 
            m.id,
            m.title,
            m.poster_file as poster_url,
            COUNT(DISTINCT mc.person_id) as shared_people
        FROM movies m
        JOIN movie_cast mc ON m.id = mc.movie_id
        WHERE mc.person_id = ANY(%s)
            AND m.id != %s
        GROUP BY m.id, m.title, m.poster_file
        HAVING COUNT(DISTINCT mc.person_id) >= %s
        ORDER BY shared_people DESC, m.title
        LIMIT %s
        """,
        (person_ids, movie_id, min_shared_people, limit),
        fetch=True
    )
    
    return [dict(r) for r in result] if result else []


def get_nexus_data(movie_id):
    """Get all data needed for the nexus visualization"""
    movie = get_movie_with_details(movie_id)
    
    if not movie:
        return None
    
    return {
        'movie': movie,
        'director': get_movie_director(movie_id),
        'actors': get_movie_actors(movie_id),
        'related_movies': get_related_movies(movie_id)
    }

def get_shared_movies_by_people(person_ids):
    """
    Find movies where ALL selected people appear together (Intersection).
    """
    if not person_ids:
        return []
    
    # Format the array for Postgres syntax
    person_ids_tuple = tuple(person_ids)
    
    query = """
        SELECT 
            m.id,
            m.title,
            m.poster_file as poster_url,
            COUNT(DISTINCT mc.person_id) as shared_count
        FROM movies m
        JOIN movie_cast mc ON m.id = mc.movie_id
        WHERE mc.person_id IN %s
        GROUP BY m.id, m.title, m.poster_file
        HAVING COUNT(DISTINCT mc.person_id) = %s
        ORDER BY m.release_date DESC
        LIMIT 10
    """
    
    # Check for single item tuple quirk in Python (1,) vs (1)
    if len(person_ids) == 1:
        # If only one person, we strictly want their movies
        query = """
            SELECT 
                m.id,
                m.title,
                m.poster_file as poster_url,
                1 as shared_count
            FROM movies m
            JOIN movie_cast mc ON m.id = mc.movie_id
            WHERE mc.person_id = %s
            ORDER BY m.release_date DESC
            LIMIT 10
        """
        params = (person_ids[0],)
    else:
        params = (person_ids_tuple, len(person_ids))

    result = execute_query(query, params, fetch=True)
    
    return [dict(r) for r in result] if result else []

def search_movies(query_text, limit=3):
    """Search for movies by title for the autocomplete"""
    if not query_text:
        return []
        
    result = execute_query(
        """
        SELECT 
            id,
            title,
            EXTRACT(YEAR FROM release_date) as year,
            poster_file as poster_url
        FROM movies 
        WHERE title ILIKE %s
        ORDER BY title ASC
        LIMIT %s
        """,
        (f'%{query_text}%', limit),
        fetch=True
    )
    
    return [dict(r) for r in result] if result else []
