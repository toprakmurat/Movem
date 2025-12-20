from src.config.database import execute_query


# ---------------------------------------------------------
# LİSTE YÖNETİMİ (Header)
# ---------------------------------------------------------

def create_custom_list_db(user_id: int, list_name: str, is_public: bool = True):
    """Create a new movie list (Ex. : 'Weekend Movies')"""
    try:
        query = """
        INSERT INTO user_lists (user_id, list_name, is_public)
        VALUES (%s, %s, %s)
        RETURNING id, list_name, is_public, created_at
        """
        params = (user_id, list_name, is_public)

        result = execute_query(query, params, fetch=True)
        if result:
            return result[0], None
        return None, "List creation failed"
    except Exception as e:
        return None, str(e)


def get_lists_by_user_db(user_id: int):
    """Get all lists created by a user"""
    try:
        query = """
        SELECT id, list_name, is_public, created_at 
        FROM user_lists 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        """
        result = execute_query(query, (user_id,), fetch=True)
        return result, None
    except Exception as e:
        return None, str(e)


def delete_list_db(list_id: int, user_id: int):
    """Delete a list (Only by the owner)"""
    try:
        # Check if list belongs to user for security
        check_query = "SELECT id FROM user_lists WHERE id = %s AND user_id = %s"
        check = execute_query(check_query, (list_id, user_id), fetch=True)

        if not check:
            return None, "List not found or permission denied"

        # Delete the list and the movies by cascade
        delete_query = "DELETE FROM user_lists WHERE id = %s RETURNING id"
        deleted = execute_query(delete_query, (list_id,), fetch=True)

        return deleted[0], None
    except Exception as e:
        return None, str(e)



def add_movie_to_list_db(list_id: int, movie_id: int):
    """Add movie to a list"""
    try:

        query = """
        INSERT INTO list_items (list_id, movie_id)
        VALUES (%s, %s)
        RETURNING list_id, movie_id, added_at
        """
        result = execute_query(query, (list_id, movie_id), fetch=True)

        if result:
            return result[0], None
        return None, "Failed to add movie"

    except Exception as e:
        if "unique constraint" in str(e).lower():
            return None, "This movie is already in the list"
        return None, str(e)


def remove_movie_from_list_db(list_id: int, movie_id: int):
    """Remove a movie from a list"""
    try:
        query = """
        DELETE FROM list_items 
        WHERE list_id = %s AND movie_id = %s
        RETURNING list_id, movie_id
        """
        result = execute_query(query, (list_id, movie_id), fetch=True)

        if result:
            return True, None
        return None, "Movie not found in list"
    except Exception as e:
        return None, str(e)


def is_movie_in_list_db(list_id: int, movie_id: int) -> bool:
    """Check if a movie is already in a list"""
    try:
        query = "SELECT 1 FROM list_items WHERE list_id = %s AND movie_id = %s"
        result = execute_query(query, (list_id, movie_id), fetch=True)
        return bool(result)
    except Exception:
        return False


def get_list_details_db(list_id: int):
    """
    [JOIN QUERY]
    Get a movie in a list with details
    """
    try:
        # Get list info
        list_info_query = "SELECT * FROM user_lists WHERE id = %s"
        list_info = execute_query(list_info_query, (list_id,), fetch=True)

        if not list_info:
            return None, "List not found"

        # Get the movies inside by joining with movies table
        movies_query = """
        SELECT 
            m.id, m.title, m.poster_file, m.release_date, s.vote_avg, li.added_at
        FROM list_items li
        JOIN movies m ON li.movie_id = m.id
        LEFT JOIN statistic s ON m.id = s.movie_id
        WHERE li.list_id = %s
        ORDER BY li.added_at DESC
        """
        movies = execute_query(movies_query, (list_id,), fetch=True)

        # Combine in a single dictionary
        result = {
            "list_info": list_info[0],
            "movies": movies if movies else []
        }

        return result, None
    except Exception as e:
        return None, str(e)


def get_public_admin_lists_db(limit: int = 6):
    """
    [JOIN QUERY]
    Get public lists created by admin users for the Collections Spotlight.
    Joins user_lists with users to filter by admin role.
    """
    try:
        query = """
        SELECT 
            ul.id,
            ul.list_name,
            ul.created_at,
            u.username as curator_name,
            COUNT(li.movie_id) as movie_count
        FROM user_lists ul
        JOIN users u ON ul.user_id = u.id
        LEFT JOIN list_items li ON ul.id = li.list_id
        WHERE ul.is_public = true AND u.role = 'admin'
        GROUP BY ul.id, ul.list_name, ul.created_at, u.username
        ORDER BY ul.created_at DESC
        LIMIT %s
        """
        result = execute_query(query, (limit,), fetch=True)
        return result if result else [], None
    except Exception as e:
        return [], str(e)