from src.config.database import execute_query

def get_favorites_db():
    """Get all favorites"""
    try:
        favorites = execute_query(
            "SELECT * FROM favorites ORDER BY id",
            fetch=True
        )
        return favorites, None
    except Exception as e:
        return None, str(e)


def get_favorite_by_id_db(id: int):
    """Get favorite by id"""
    try:
        fav = execute_query(
            "SELECT * FROM favorites WHERE id = %s",
            (id,),
            fetch=True
        )
        if fav:
            return fav[0], None
        return None, None
    except Exception as e:
        return None, str(e)


def create_favorite_db(data: dict):
    """Create a new favorite"""
    try:
        new_fav = execute_query(
            """
            INSERT INTO favorites (user_id, movie_id)
            VALUES (%s, %s)
            RETURNING id, user_id, movie_id, created_at
            """,
            (
                data.get("user_id"),
                data.get("movie_id")
            ),
            fetch=True
        )
        if new_fav:
            return new_fav[0], None
        return None, "Failed to create favorite"
    except Exception as e:
        return None, str(e)


def update_favorite_db(id: int, data: dict):
    """Update an existing favorite"""
    try:
        existing, err = get_favorite_by_id_db(id)
        if err:
            return None, err
        if not existing:
            return None, None
        
        update_fields = []
        params = []

        if "user_id" in data:
            update_fields.append("user_id = %s")
            params.append(data["user_id"])

        if "movie_id" in data:
            update_fields.append("movie_id = %s")
            params.append(data["movie_id"])

        if not update_fields:
            return existing, None
        
        params.append(id)

        updated = execute_query(
            f"""
            UPDATE favorites
            SET {", ".join(update_fields)}
            WHERE id = %s
            RETURNING id, user_id, movie_id, created_at
            """,
            tuple(params),
            fetch=True
        )

        if updated:
            return updated[0], None
        return None, "Failed to update"
    except Exception as e:
        return None, str(e)


def delete_favorite_db(id: int):
    """Delete favorite by id"""
    try:
        deleted = execute_query(
            "DELETE FROM favorites WHERE id = %s RETURNING *",
            (id,),
            fetch=True
        )
        if deleted:
            return deleted[0], None
        return None, "Favorite not found"
    except Exception as e:
        return None, str(e)
    

def is_movie_favorite_for_user(user_id: int, movie_id: int) -> bool:
    """Return True if the movie is in the given user's favorites"""
    try:
        fav = execute_query(
            "SELECT 1 FROM favorites WHERE user_id = %s AND movie_id = %s",
            (user_id, movie_id),
            fetch=True
        )
        return bool(fav)
    except Exception:
        return False


