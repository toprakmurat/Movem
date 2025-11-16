from src.config.database import execute_query

def get_movies_db():
    """Get all movies"""
    try:
        movies = execute_query(
            """
            SELECT id, title, overview, tagline, release_date, poster_file, banner_file, platform_id 
            FROM movies
            ORDER BY title
            """,
            fetch=True
        )
        return movies, None
    except Exception as e:
        return None, str(e)


def get_movie_by_id_db(id: int):
    """Get movie by id"""
    try:
        movies = execute_query(
            """
            SELECT id, title, overview, tagline, release_date, poster_file, banner_file, platform_id 
            FROM movies
            WHERE id = %s
            """,
            (id,),
            fetch=True
        )
        if movies:
            return movies[0], None 
        return None, "Movie not found"
    except Exception as e:
        return None, str(e)


def create_movie_db(movie_data: dict):
    """Create a new movie"""
    try:
        new_movie = execute_query(
            """
            INSERT INTO movies(title, overview, tagline, release_date, poster_file, banner_file, platform_id)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, overview, tagline, release_date, poster_file, banner_file, platform_id, created_at
            """,
            (
                movie_data.get('title'),
                movie_data.get('overview'),
                movie_data.get('tagline'),
                movie_data.get('release_date'),
                movie_data.get('poster_file'),
                movie_data.get('banner_file'),
                movie_data.get('platform_id')
            ),
            fetch=True
        )

        if new_movie:
            return new_movie[0], None
        return None, "Failed to create movie"
    except Exception as e:
        return None, str(e)


def update_movie_db(id: int, movie_data: dict):
    """Update the movie with given id and return updated one"""
    try:
        existing_movie, err = get_movie_by_id(id)
        if err:
            return None, err
        if not existing_movie:
            return None, "Movie not found"
        
        update_fields = []
        params = []

        for key in ['title', 'overview', 'tagline', 'release_date', 'poster_file', 'banner_file', 'platform_id']:
            if key in movie_data:
                update_fields.append(f"{key} = %s")
                params.append(movie_data[key])

        if not update_fields:
            return existing_movie, None
        params.append(id) 

        updated_movie = execute_query(
            f"""
            UPDATE movies
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, title, overview, tagline, release_date, poster_file, banner_file, platform_id, created_at
            """,
            tuple(params),
            fetch=True
        )

        return updated_movie[0], None

    except Exception as e:
        return None, str(e)


def delete_movie_db(id: int):
    """Delete a movie by id"""
    try:
        deleted_movie = execute_query(
            """
            DELETE FROM movies
            WHERE id = %s
            RETURNING id, title, overview, tagline, release_date, poster_file, banner_file, platform_id, created_at
            """,
            (id,),
            fetch=True
        )

        if deleted_movie:
            return deleted_movie[0], None
        return None, "Movie not found"

    except Exception as e:
        return None, str(e)

def get_genres_by_id(id:int):
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
        return None, "Genre not found"
    except Exception as e:
        return None, str(e)
    
def get_movies_by_genre_db(genre_id: int):
    """Get movies by genre ID"""
    try:
        genre, err = get_genres_by_id(genre_id)
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
