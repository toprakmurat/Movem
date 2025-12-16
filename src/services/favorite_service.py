from src.config.database import execute_query
from src.utils.pagination_utils import Pagination

######################### CRUD FOR FAVORITES ##########################
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
    

#########################  COMPLEX ONES ##########################

def get_favorites_paginated_db(page: int = 1, per_page: int = 20):
    try:
        offset = (page - 1) * per_page
        
        count_res = execute_query("SELECT COUNT(*) as count FROM favorites", fetch=True)
        total = count_res[0]['count'] if count_res else 0

        favorites = execute_query(
            "SELECT * FROM favorites ORDER BY id LIMIT %s OFFSET %s",
            (per_page, offset),
            fetch=True
        ) or []

        return Pagination(items=favorites, page=page, per_page=per_page, total_count=total), None
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


def get_favorite_movies_detailed_for_user_db(user_id: int):
    """
    Return detailed favorites for a specific user
    """
    try:
        favs = execute_query(
            """
            SELECT
                f.id AS favorite_id,
                f.user_id,
                f.movie_id,
                m.title AS movie_title,
                m.poster_file AS movie_poster,
                m.release_date,
                s.vote_avg,
                s.runtime
            FROM favorites f
            JOIN movies m ON m.id = f.movie_id
            LEFT JOIN statistic s ON m.id = s.movie_id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
            """,
            (user_id,),
            fetch=True
        )

        if not favs:
            return [], None

        fav_list = []
        for f in favs:
            fav_list.append({
                "favorite_id": f["favorite_id"],
                "user_id": f["user_id"],
                "movie_id": f["movie_id"],
                "movie_title": f["movie_title"],
                "movie_poster": f["movie_poster"],
                "release_date": f["release_date"],
                "rating": float(f.get("vote_avg") or 0),
                "runtime": float(f.get("runtime") or 0)
            })

        return fav_list, None

    except Exception as e:
        return None, str(e)



def toggle_favorite_db(user_id: int, movie_id: int):
    """
    Toggle favorite
    """

    try:
        favorites, err = get_favorites_db()
        if err:
            return None, err

        existing = None
        for fav in favorites:
            if fav["user_id"] == user_id and fav["movie_id"] == movie_id:
                existing = fav
                break

        if existing:
            deleted, err = delete_favorite_db(existing["id"])
            if err:
                return None, err
            return {
                "action": "removed",
                "favorite": deleted
            }, None

        new_fav, err = create_favorite_db({
            "user_id": user_id,
            "movie_id": movie_id
        })
        if err:
            return None, err

        return {
            "action": "added",
            "favorite": new_fav
        }, None


    except Exception as e:
        return None, str(e)
