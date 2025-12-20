from src.config.database import execute_query
from src.services.favorite_service import *
from src.services.nexus_service import *
from src.services.genres_service import *
from flask_login import current_user
from src.utils.pagination_utils import Pagination


######################### CRUD FOR MOVIES ##########################

def get_movies_db():
    """Get all movies"""
    try:
        movies = execute_query(
            """
            SELECT *
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
            SELECT *
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

        for key in ['title', 'overview', 'tagline', 'release_date', 'poster_file', 'banner_file', 'platform_id', 'created_at']:
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


######################### COMPLEX ONES ##########################

def get_movies_paginated_db(page: int = 1, per_page: int = 8, 
                            genre_id: int = None, sort_by: str = None, 
                            search: str = None, 
                            rating_min: float = 0, rating_max: float = 10, 
                            runtime_min: int = 0, runtime_max: int = 300): 
    try:
        offset = (page - 1) * per_page
        
        where_clauses = ["1=1"] 
        where_params = []
        order_params = []
        order_parts = []
        
        joins = ["LEFT JOIN statistic s ON m.id = s.movie_id"]
        
        if genre_id:
            joins.append("JOIN movies_genres mg ON m.id = mg.movie_id")
            where_clauses.append("mg.genre_id = %s")
            where_params.append(genre_id)

        join_sql = " ".join(joins)

        if search:
            keyword = f"%{search}%"
            where_clauses.append("(m.title ILIKE %s OR m.overview ILIKE %s)")
            where_params.extend([keyword, keyword])

            order_parts.append("""
                CASE
                    WHEN m.title ILIKE %s THEN 1
                    WHEN m.overview ILIKE %s THEN 2
                    ELSE 3
                END
            """)
            order_params.extend([keyword, keyword])

        if rating_min > 0 or rating_max < 10:
            where_clauses.append("s.vote_avg >= %s")
            where_params.append(rating_min)
            where_clauses.append("s.vote_avg <= %s")
            where_params.append(rating_max)
        
        if runtime_min > 0 or runtime_max < 300:
            where_clauses.append("s.runtime >= %s")
            where_params.append(runtime_min)
            where_clauses.append("s.runtime <= %s")
            where_params.append(runtime_max)

        where_sql = "WHERE " + " AND ".join(where_clauses)

        if sort_by in ("rating_desc", "rating"):
            order_parts.append("s.vote_avg DESC")
        elif sort_by == "rating_asc":
            order_parts.append("s.vote_avg ASC")
        elif sort_by in ("release_desc", "release"):
            order_parts.append("m.release_date DESC")
        elif sort_by == "release_asc":
            order_parts.append("m.release_date ASC")
        else:
            order_parts.append("m.title ASC")

        order_sql = "ORDER BY " + ", ".join(order_parts)

        count_sql = f"""
            SELECT COUNT(DISTINCT m.id) as count
            FROM movies m
            {join_sql}
            {where_sql}
        """
        total_result = execute_query(count_sql, tuple(where_params), fetch=True)
        total_count = total_result[0]['count'] if total_result else 0

        data_sql = f"""
            SELECT m.*, m.poster_file as poster_path, 
                            s.vote_avg as rating, s.vote_count, s.runtime
            FROM movies m
            {join_sql}
            {where_sql}
            {order_sql}
            LIMIT %s OFFSET %s
        """
        
        data_params = tuple(where_params + order_params +[per_page, offset])
        
        movies = execute_query(data_sql, data_params, fetch=True) or []

        return Pagination(items=movies,
                          page=page,
                          per_page=per_page,
                          total_count=total_count), None

    except Exception as e:
        print("DB Error:", e)
        return Pagination(items=[], page=page, per_page=per_page, total_count=0), str(e)

def get_movie_details_full_db(movie_id: int, current_user_id: int):
    """ Get movies, statistics, genres, platform and favorite_count data as movie_data"""

    try:
        detailed_movies = execute_query(
            """
            SELECT
                m.id            AS id,
                m.title         AS title,
                m.overview      AS overview,
                m.tagline       AS tagline,
                m.release_date  AS release_date,
                m.poster_file   AS poster,
                m.banner_file   AS banner,

                (
                    SELECT COUNT(DISTINCT f.user_id)
                    FROM favorites f
                    WHERE f.movie_id = m.id
                )               AS favorite_count,

                s.runtime       AS runtime,
                s.vote_avg      AS vote_avg,
                s.vote_count    AS vote_count,
                s.budget        AS budget,
                s.revenue       AS revenue,

                p.platform_name AS platform_name,
                p.logo_path     AS platform_logo

            FROM movies m
            LEFT JOIN statistic s
                ON s.movie_id = m.id
            LEFT JOIN platforms p
                ON p.id = m.platform_id
            WHERE m.id = %s
            """,
            (movie_id,),
            fetch=True)
        
        if not detailed_movies:
            return None, "Movie not found!"
        
        row = detailed_movies[0]
        
        genres_for_movies = execute_query(
            """
            SELECT 
                g.genre_name 

            FROM genres g
            JOIN movies_genres mg 
                ON g.id = mg.genre_id
            WHERE mg.movie_id = %s

            """,
            (movie_id,),
            fetch=True)
        
        genre_list = [g["genre_name"] for g in genres_for_movies]
        
        if current_user_id:
            is_favorite = is_movie_favorite_for_user(current_user_id, movie_id)
        else:
            is_favorite = False

        movie_data = {
            "id": row["id"],
            "title": row["title"],
            "overview": row["overview"],
            "tagline": row["tagline"],
            "release_date": row["release_date"],
            "poster_file": row["poster"],
            "banner_file": row["banner"],

            # genres & favorite
            "genre_list": genre_list,
            "is_favorite": is_favorite,
            "favorite_count": row["favorite_count"],

            # statistics
            "runtime": row["runtime"],
            "vote_avg": row["vote_avg"],
            "vote_count": row["vote_count"],
            "budget": (
                f"${row['budget']:,.0f}".replace(",", ".")
                if row["budget"] is not None
                else "Unknown"
            ),
            "revenue": (
                f"${row['revenue']:,.0f}".replace(",", ".")
                if row["revenue"] is not None
                else "Unknown"
            ),

            # providers
            "platform_name": row["platform_name"],
            "platform_logo": row["platform_logo"]
        }

        return movie_data, None
    except Exception as e:
        return None, str(e)

def get_recommendations_db(movie_id: int, current_user_id: int):
    # Scoring Logic:
    # 1. Similar Users: +5 points (If another user favorited this movie, their other favorites get points)
    # 2. Same Director: +30 points
    # 3. Same Genre:    +10 points (Cumulative for each matching genre)
    # 4. Same Platform: +3 points
    # 5. Same Actor:    +5 points
    # Max score is 100
    
    try:
        sql = """
        SELECT 
            m.id,
            m.title,
            m.poster_file,
            m.release_date,
            s.vote_avg,
            STRING_AGG(DISTINCT g.genre_name, ', ') as genres,
            
            LEAST(final_scores.total_score, 100) as match_score

        FROM (
            SELECT 
                movie_id, 
                SUM(score) as total_score 
            FROM (
                -- Other favorites of favorited users
                SELECT f2.movie_id, 5 as score
                FROM favorites f1
                JOIN favorites f2 ON f1.user_id = f2.user_id
                WHERE f1.movie_id = %s AND f2.movie_id != %s
                
                UNION ALL
                
                -- Same director
                SELECT mc2.movie_id, 30 as score
                FROM movie_cast mc1
                JOIN movie_cast mc2 ON mc1.person_id = mc2.person_id
                WHERE mc1.movie_id = %s 
                AND mc2.movie_id != %s
                AND mc1.role = 'Director' 
                AND mc2.role = 'Director'
                
                UNION ALL
                
                -- Same genres
                SELECT mg2.movie_id, 10 as score
                FROM movies_genres mg1
                JOIN movies_genres mg2 ON mg1.genre_id = mg2.genre_id
                WHERE mg1.movie_id = %s AND mg2.movie_id != %s

                UNION ALL
                
                -- Same platform
                SELECT m2.id as movie_id, 3 as score
                FROM movies m1
                JOIN movies m2 ON m1.platform_id = m2.platform_id
                WHERE m1.id = %s AND m2.id != %s

                UNION ALL

                -- Same actors (+5 per shared actor)
                SELECT mc2.movie_id, 5 as score
                FROM movie_cast mc1
                JOIN movie_cast mc2 
                    ON mc1.person_id = mc2.person_id
                WHERE mc1.movie_id = %s
                AND mc2.movie_id != %s
                AND mc1.role != 'Director'
                AND mc2.role != 'Director'
            ) raw_scores
            GROUP BY movie_id
        ) AS final_scores
        
        JOIN movies m
            ON final_scores.movie_id = m.id
        LEFT JOIN statistic s 
            ON m.id = s.movie_id
        JOIN movies_genres mg
            ON m.id = mg.movie_id
        JOIN genres g
            ON mg.genre_id = g.id
        
        WHERE m.id NOT IN (
            SELECT movie_id FROM favorites WHERE user_id = %s
        ) AND s.vote_count>1000
        
        GROUP BY m.id, m.title, m.poster_file, m.release_date, s.vote_avg, final_scores.total_score
        ORDER BY match_score DESC, s.vote_avg DESC
        LIMIT 5;
        """
        
        params = (movie_id, movie_id, movie_id, movie_id, movie_id, movie_id, movie_id, movie_id, movie_id, movie_id, current_user_id)
        
        recommendations = execute_query(sql, params, fetch=True)
        return recommendations, None

    except Exception as e:
        return [], str(e)

def get_best_movies_detailed_db(limit: int = 10):
    """
    Get top trending movies by vote_avg
    """
    try:
        movies = execute_query("""
        SELECT 
            m.id, m.title, m.tagline,
            m.poster_file as poster_url, m.banner_file as backdrop_url,
            m.release_date, s.vote_avg, s.runtime
        FROM movies m
        JOIN statistic s
            ON m.id = s.movie_id
        WHERE s.vote_count > 1000
        ORDER BY s.vote_avg DESC, s.vote_count DESC
        LIMIT %s;
        """,
        (limit,),
        fetch=True)

        if not movies:
            return [], None

        movie_ids = [movie["id"] for movie in movies]
        
        genre_map = {}
        if movie_ids:
            genre_rows = execute_query("""
                SELECT mg.movie_id, g.genre_name
                FROM movies_genres mg
                JOIN genres g ON mg.genre_id = g.id
                WHERE mg.movie_id = ANY(%s)
            """, (movie_ids,), fetch=True)

            for row in genre_rows:
                genre_map.setdefault(row["movie_id"], []).append(row["genre_name"])

        movie_list = []
        for m in movies:
            movie_list.append({
                "id": m["id"],
                "title": m["title"],
                "release_date": m["release_date"],
                "tagline": m.get("tagline"),
                "poster_file": m.get("poster_url"),
                "banner_file": m.get("backdrop_url"),
                "rating": float(m.get("vote_avg") or 0),
                "runtime": float(m.get("runtime") or 0),
                "genre_list": genre_map.get(m["id"], [])
            })
        
        return movie_list, None

    except Exception as e:
        return [], str(e)


def get_best_movies_for_genres_detailed_db(limit_per_genre: int = 10, top_genres_limit: int = 6):
    """
    Get top-rated movies from the most popular genres.
    """
    try:
        top_genres, error = get_top_genres_db(limit=top_genres_limit)
        
        if error:
            return [], error
        if not top_genres:
            return [], None

        all_movies = []
        seen_movie_ids = set()  

        for genre in top_genres:
            gid = genre['genre_id']
            
            movie_sql = """
            SELECT 
                m.id, m.title, m.tagline, m.overview,
                m.poster_file, m.banner_file, m.release_date,
                COALESCE(s.vote_avg, 0) as rating,
                COALESCE(s.runtime, 0) as runtime,
                COALESCE(s.budget, 0) as budget,      
                COALESCE(s.revenue, 0) as revenue,   
                array_agg(DISTINCT g.genre_name) as genre_list

            FROM movies m
            LEFT JOIN statistic s
                ON m.id = s.movie_id
            LEFT JOIN movies_genres mg
                ON m.id = mg.movie_id
            JOIN genres g
                ON mg.genre_id = g.id
            
            WHERE m.id IN (
                SELECT movie_id FROM movies_genres WHERE genre_id = %s
            ) 
            AND s.vote_count > 1000
            
            GROUP BY m.id, s.id
            ORDER BY s.vote_avg DESC
            LIMIT %s;
            """
            
            genre_movies = execute_query(movie_sql, (gid, limit_per_genre), fetch=True) or []

            for movie in genre_movies:
                if movie["id"] not in seen_movie_ids:
                    all_movies.append(movie)
                    seen_movie_ids.add(movie["id"])

        return all_movies, None

    except Exception as e:
        return [], str(e)

def get_tonights_pick_director_detailed_db():
    try:
        sql = """
        WITH top_directors AS (
            SELECT 
                mc.person_id, 
                p.name AS director_name,
                AVG(s.vote_avg) as avg_rating,
                SUM(s.vote_count) as total_votes
            FROM movie_cast mc
            JOIN people p ON mc.person_id = p.id
            JOIN statistic s ON mc.movie_id = s.movie_id
            WHERE mc.role = 'Director'
            GROUP BY mc.person_id, p.name
            HAVING COUNT(DISTINCT mc.movie_id) >= 4 
               AND AVG(s.vote_avg) >= 7.0
               AND SUM(s.vote_count) >= 1000
        ),
        daily_selection AS (
            SELECT person_id, director_name 
            FROM top_directors
            ORDER BY md5(person_id::text || CURRENT_DATE::text)
            LIMIT 1
        )
        SELECT
            m.id,
            m.title,
            m.tagline,
            m.release_date,
            m.poster_file,
            m.banner_file,
            COALESCE(s.vote_avg, 0) AS vote_avg,
            COALESCE(s.runtime, 0) AS runtime,
            array_agg(DISTINCT g.genre_name) AS genre_list,
            (SELECT director_name FROM daily_selection) AS director_name
        FROM movies m
        JOIN movie_cast mc ON mc.movie_id = m.id
        JOIN statistic s ON s.movie_id = m.id
        LEFT JOIN movies_genres mg ON mg.movie_id = m.id
        LEFT JOIN genres g ON g.id = mg.genre_id
        WHERE mc.role = 'Director'
          AND mc.person_id = (SELECT person_id FROM daily_selection)
        GROUP BY m.id, s.vote_avg, s.runtime
        ORDER BY s.vote_avg DESC
        LIMIT 10;
        """

        result = execute_query(sql, fetch=True)

        if not result:
            return [], None 

        movies = []
        for row in result:
            movies.append({
                "id": row["id"],
                "title": row["title"],
                "release_date": row["release_date"],
                "tagline": row.get("tagline"),
                "poster_file": row.get("poster_file"),
                "rating": float(row.get("vote_avg") or 0),
                "genre_list": row.get("genre_list") or [],
                "director_name": row.get("director_name"),
                "runtime": float(row.get("runtime") or 0),
            })

        return movies, None

    except Exception as e:
        return [], str(e)


def get_random_movies_detailed_db(limit: int = 8):
    """
    Get random movies with statistics and genres.
    """
    try:
        movies = execute_query("""
            SELECT m.id, m.title, m.tagline,
                   m.poster_file as poster_url, m.banner_file as backdrop_url,
                   m.release_date, s.vote_avg, s.runtime
            FROM movies m
            LEFT JOIN statistic s ON m.id = s.movie_id
            ORDER BY RANDOM()
            LIMIT %s
        """, (limit,), fetch=True)

        if not movies:
            return [], None

        movie_ids = [m["id"] for m in movies]
        genre_rows = execute_query("""
            SELECT mg.movie_id, g.genre_name
            FROM movies_genres mg
            JOIN genres g ON mg.genre_id = g.id
            WHERE mg.movie_id = ANY(%s)
        """, (movie_ids,), fetch=True)

        genre_map = {}
        for row in genre_rows:
            genre_map.setdefault(row["movie_id"], []).append(row["genre_name"])

        movie_list = []
        for m in movies:
            movie_list.append({
                "id": m["id"],
                "title": m["title"],
                "release_date": m["release_date"],
                "tagline": m.get("tagline"),
                "poster_file": m.get("poster_url"),
                "banner_file": m.get("backdrop_url"),
                "rating": float(m.get("vote_avg") or 0),
                "runtime": float(m.get("runtime") or 0),
                "genre_list": genre_map.get(m["id"], [])
            })

        return movie_list, None

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
    """Creates a new platform with MANDATORY ID"""
    try:
        platform_name = platform_data.get('platform_name')
        logo_path = platform_data.get('logo_path', None)
        platform_id = platform_data.get('id')  

        if not platform_id:
            return None, "Platform ID is required!"

        query = """
        INSERT INTO platforms (id, platform_name, logo_path)
        VALUES (%s, %s, %s)
        RETURNING *
        """
        params = (platform_id, platform_name, logo_path)

        new_platform = execute_query(query, params, fetch=True)
        if new_platform:
            try:
                execute_query("SELECT setval('platforms_id_seq', (SELECT MAX(id) FROM platforms))", fetch=False)
            except Exception:
                pass 

            return new_platform[0], None
            
        return None, "Failed to create platform"
        
    except Exception as e:
        if "duplicate key" in str(e):
            return None, f"Platform ID {platform_id} already exists!"
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
    """Deletes a platform by its ID """
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
