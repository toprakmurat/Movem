from src.config.database import execute_query
from src.utils.pagination_utils import Pagination

######################### CRUD FOR GENRES ##########################

def get_genres_db():
    """Get all genres"""
    try:
        genres = execute_query(
        """
        SELECT *
        FROM genres
        ORDER BY genre_name ASC
        """,
        fetch=True)
        if genres is not None:
            return genres, None
        return [], None
    except Exception as e:
        return None, str(e)

def get_genres_paginated_db(page: int = 1, per_page: int = 20):
    try:
        offset = (page - 1) * per_page
        
        # Count
        count_res = execute_query("SELECT COUNT(*) as count FROM genres", fetch=True)
        total = count_res[0]['count'] if count_res else 0

        # Data
        genres = execute_query(
            "SELECT * FROM genres ORDER BY id LIMIT %s OFFSET %s",
            (per_page, offset),
            fetch=True
        ) or []

        return Pagination(items=genres, page=page, per_page=per_page, total_count=total), None
    except Exception as e:
        return None, str(e)

def create_genre_db(genre_data:dict):
    """Get a new genre"""
    try:
        genres = execute_query(
        """
        INSERT INTO genres(id, genre_name)
        VALUES (%s, %s)
        RETURNING id, genre_name
        """,
        (   
        genre_data.get
        ('id'),
        genre_data.get
        ('genre_name'),
        ),
        fetch=True)

        if genres:
            return genres[0], None
        return None, "Failed to create genre"
    except Exception as e:
        return None, str(e)
    
def update_genre_db(id: int, genre_data: dict):
    """Update the genre with given id and return updated one"""
    try:
        existing_genre, err = get_genres_by_id_db(id)
        if err:
            return None, err
        if not existing_genre:
            return None, None

        update_fields = []
        params = []

        if 'genre_name' in genre_data:
            update_fields.append("genre_name = %s")
            params.append(genre_data['genre_name'])

        if not update_fields:
            return existing_genre, None

        params.append(id)  

        updated_genre = execute_query(
            f"""
            UPDATE genres
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, genre_name
            """,
            tuple(params),
            fetch=True
        )

        if updated_genre:
            return updated_genre[0], None
        return None, "Failed to update genre"

    except Exception as e:
        return None, str(e)


def delete_genre_db(id: int):
    """Delete a genre by id"""
    try:
        deleted_genre = execute_query(
            """
            DELETE FROM genres
            WHERE id = %s
            RETURNING id, genre_name
            """,
            (id,),
            fetch=True
        )

        if deleted_genre:
            return deleted_genre[0], None
        return None, "Genre not found"

    except Exception as e:
        return None, str(e)

######################### CRUD FOR MOVIES_GENRES ##########################

def get_movies_genres_db():
    """Get all movie-genre relationships"""
    try:
        movie_genres = execute_query(
            "SELECT id, movie_id, genre_id FROM movies_genres",
            fetch=True
        )
        return movie_genres, None
    except Exception as e:
        return None, str(e)

def get_movies_genres_paginated_db(page: int = 1, per_page: int = 20):
    try:
        offset = (page - 1) * per_page
        
        count_res = execute_query("SELECT COUNT(*) as count FROM movies_genres", fetch=True)
        total = count_res[0]['count'] if count_res else 0

        data = execute_query(
            "SELECT * FROM movies_genres ORDER BY id LIMIT %s OFFSET %s",
            (per_page, offset),
            fetch=True
        ) or []

        return Pagination(items=data, page=page, per_page=per_page, total_count=total), None
    except Exception as e:
        return None, str(e)

def create_movie_genre_db(movies_genre_data:dict):
    """Create a new movie-genre relationship"""
    try:
        movies_genres = execute_query(
        """
        INSERT INTO movies_genres(movie_id, genre_id)
        VALUES (%s, %s)
        RETURNING id, movie_id, genre_id
        """,
        (   
        movies_genre_data.get
        ('movie_id'),
        movies_genre_data.get
        ('genre_id'),
        ),
        fetch=True)

        if movies_genres:
            return movies_genres[0], None
        return None, "Failed to create movie-genre relationship"
    except Exception as e:
        return None, str(e)

    
def update_movie_genre_db(id: int, data: dict):
    """Update a movie-genre relation by id and return updated one"""
    try:

        existing, err = get_movies_genres_by_id_db(id)
        if err:
            return None, err
        if not existing:
            return None, None
        
        update_fields = []
        params = []

        if 'movie_id' in data:
            update_fields.append("movie_id = %s")
            params.append(data['movie_id'])

        if 'genre_id' in data:
            update_fields.append("genre_id = %s")
            params.append(data['genre_id'])

        if not update_fields:
            return existing, None

        params.append(id)

        updated = execute_query(
            f"""
            UPDATE movies_genres
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, movie_id, genre_id
            """,
            tuple(params),
            fetch=True
        )

        if updated:
            return updated[0], None
        
        return None, "Failed to update movie-genre relationship"

    except Exception as e:
        return None, str(e)



def delete_movie_genre_db(id: int):
    """Delete a movie-genre relationship"""
    try:
        deleted = execute_query(
            """
            DELETE FROM movies_genres
            WHERE id = %s
            RETURNING id, movie_id, genre_id
            """,
            (id,),
            fetch=True
        )
        if deleted:
            return deleted[0], None
        return None, None
    except Exception as e:
        return None, str(e)


######################### COMPLEX ONES ##########################

def get_top_genres_db(limit: int = 5):
    """
    Get top genres by number of movies in each genre.
    """
    try:
        top_genres = execute_query(
            """
            SELECT 
                g.id AS genre_id,
                g.genre_name,
                COUNT(mg.movie_id) AS movie_count
            FROM genres g
            LEFT JOIN movies_genres mg
                ON g.id = mg.genre_id
            GROUP BY g.id, g.genre_name
            ORDER BY movie_count DESC, g.genre_name ASC
            LIMIT %s;
            """,
            (limit,),
            fetch=True
        )
        if top_genres is not None:
            return top_genres, None
        return [], None
    except Exception as e:
        return None, str(e)


def get_genres_for_movie(movie_id: int):
    """
    Returns a list of genre names for a given movie.
    Example: ["Action", "Drama", "Sci-Fi"]
    """
    try:
        rows = execute_query(
            """
            SELECT g.genre_name
            FROM genres g
            JOIN movies_genres mg
                ON mg.genre_id = g.id
            WHERE mg.movie_id = %s
            """,
            (movie_id,),
            fetch=True
        ) or []

        return [row["genre_name"] for row in rows]

    except Exception as e:
        return []
    

def get_genres_by_id_db(id:int):
    """Get genres by id"""

    try:
        genres = execute_query(
        """
        SELECT *
        FROM genres
        WHERE id = %s
        """,
        (id,),
        fetch=True)
        if genres:
            return genres[0], None
        return None, None
    except Exception as e:
        return None, str(e)
    

def get_movies_genres_by_id_db(id: int):
    """Get a movie-genre relationship by id"""
    try:
        rows = execute_query(
            """
            SELECT id, movie_id, genre_id
            FROM movies_genres
            WHERE id = %s
            """,
            (id,),
            fetch=True
        )
        if rows:
            return rows[0], None
        return None, None
    except Exception as e:
        return None, str(e)

    
def get_movies_by_genre_db(genre_id: int):
    """Get movies by genre ID"""
    try:
        genre, err = get_genres_by_id_db(genre_id)
        if err:
            return None, err
        if not genre:
            return None, "Genre not found"
        
        movies = execute_query(
            """
            SELECT movies.id AS movie_id, movies.title, movies.overview, movies.tagline, movies.release_date, movies.poster_file, movies.banner_file, movies.platform_id
            FROM movies, movies_genres
            WHERE movies.id = movies_genres.movie_id
              AND movies_genres.genre_id = %s
            ORDER BY movies.title
            """,
            (genre_id,),
            fetch=True
        )
        if movies:
            return movies, None
        return None, "No movies in this genre"
    except Exception as e:
        return None, str(e)
