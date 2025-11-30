from src.config.database import execute_query
from typing import List, Any
from dataclasses import dataclass

@dataclass
class Pagination:
    items: List[Any]
    page: int = 1
    per_page: int = 8
    total_count: int = 0

    @property
    def total(self) -> int:
        return self.total_count

    def start_index(self) -> int:
        if not self.items:
            return 0
        return (self.page - 1) * self.per_page + 1

    def end_index(self) -> int:
        return min(self.page * self.per_page, self.total_count)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.end_index() < self.total_count

    @property
    def prev_num(self) -> int:
        return max(1, self.page - 1)

    @property
    def next_num(self) -> int:
        return self.page + 1
    

######################### MOVIES ##########################

def get_movies_paginated_db(page: int = 1, per_page: int = 8):
    try:
        total_result = execute_query("SELECT COUNT(*) as count FROM movies", fetch=True)
        total_count = total_result[0]['count'] if total_result else 0

        offset = (page - 1) * per_page
        movies = execute_query(
            "SELECT * FROM movies ORDER BY title LIMIT %s OFFSET %s",
            (per_page, offset),
            fetch=True
        ) or []

        return Pagination(items=movies, page=page, per_page=per_page, total_count=total_count), None
    except Exception as e:
        return Pagination(items=[], page=page, per_page=per_page, total_count=0), str(e)

    
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
        
        if movies and isinstance(movies, list):
            return movies[0], None
        return None, None
    except Exception as e:
        return None, str(e)



def create_movie_db(movie_data: dict):
    """Create a new movie"""
    try:
        new_movie = execute_query(
            """
            INSERT INTO movies(id, title, overview, tagline, release_date, poster_file, banner_file, platform_id)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, overview, tagline, release_date, poster_file, banner_file, platform_id, created_at
            """,
            (   
                movie_data.get
                ('id'),
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
        existing_movie, err = get_movie_by_id_db(id)
        if err:
            return None, err
        if not existing_movie:
            return None, None
        
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
        return None, None

    except Exception as e:
        return None, str(e)

######################### GENRES ##########################
def get_genres_db():
    """Get all genres"""
    try:
        genres = execute_query(
        """
        SELECT *
        FROM genres
        """,
        fetch=True)
        if genres:
            return genres, None
        return None, None
    except Exception as e:
        return None, str(e)
    

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
######################### MOVIES_GENRES ##########################

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

######################### MIXED ##########################    
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
    
# Platforms CRUD operations

def get_platforms():
    """Gets all platforms"""
    try:
        platforms = execute_query(
            "SELECT id, platform_name, logo_path FROM platforms ORDER BY platform_name ASC",
            fetch=True
        )
        return platforms, None
    except Exception as e:
        return None, str(e)


def get_platform_by_id(platform_id):
    """Gets a single platform by its ID"""
    try:
        platform = execute_query(
            "SELECT id, platform_name, logo_path FROM platforms WHERE id = %s",
            (platform_id,),
            fetch=True
        )
        if platform:
            return platform[0], None
        return None, "Platform not found"
    except Exception as e:
        return None, str(e)


def create_platform(platform_data):
    """Creates a new platform"""
    try:
        platform_name = platform_data.get('platform_name')
        logo_path = platform_data.get('logo_path', None)
        
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
            return new_platform[0], None
        return None, "Failed to create platform"
    except Exception as e:
        return None, str(e)


def update_platform(platform_id, platform_data):
    """Updates an existing platform"""
    try:
        platform_check, err = get_platform_by_id(platform_id)
        if err:
            return None, err
        if not platform_check:
            return None, "Platform not found"
            
        update_fields = []
        params = []
        
        if 'platform_name' in platform_data:
            update_fields.append("platform_name = %s")
            params.append(platform_data['platform_name'])
        if 'logo_path' in platform_data:
            update_fields.append("logo_path = %s")
            params.append(platform_data['logo_path'])
            
        if not update_fields:
            return platform_check, None

        params.append(platform_id)
        
        query = f"""
            UPDATE platforms
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        
        updated_platform = execute_query(query, tuple(params), fetch=True)
        
        if updated_platform:
            return updated_platform[0], None
        return None, "Failed to update platform"
    except Exception as e:
        return None, str(e)


def delete_platform_by_id(platform_id):
    """Deletes a platform by its ID"""
    try:
        deleted_platform = execute_query(
            "DELETE FROM platforms WHERE id = %s RETURNING *",
            (platform_id,),
            fetch=True
        )
        if deleted_platform:
            return deleted_platform[0], None
        return None, "Platform not found"
    except Exception as e:
        return None, str(e)
