from src.config.database import execute_query

def get_users_db():
    """Get all users"""
    try:
        users = execute_query("SELECT * FROM users", fetch=True)
        return users, None
    except Exception as e:
        return None, str(e)

def get_user_by_id_db(id: int):
    """Get user by id"""
    try:
        users = execute_query("SELECT * FROM users WHERE id = %s", (id,), fetch=True)
        if users:
            return users[0], None
        return None, "User not found"
    except Exception as e:
        return None, str(e)


def create_user_db(user_data: dict):
    try:
        profile_pic = user_data.get('profile_picture', 'img/placeholder_avatar.svg')

        query = """
            INSERT INTO users(username, email, first_name, last_name, password_hash, role, game_score, profile_picture)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, role
        """
        params = (
            user_data.get('username'),
            user_data.get('email'),
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('password_hash'),
            'user',
            0,
            profile_pic
        )
        new_user = execute_query(query, params, fetch=True)
        if new_user:
            return new_user[0], None
        return None, "Failed to create user"
    except Exception as e:
        return None, str(e)


def update_user_db(id: int, user_data: dict):
    try:
        existing, err = get_user_by_id_db(id)
        if not existing: return None, "User not found"

        update_fields = []
        params = []
        allowed = ['first_name', 'last_name', 'bio', 'profile_picture', 'username']

        for key in allowed:
            if key in user_data:
                update_fields.append(f"{key} = %s")
                params.append(user_data[key])

        if not update_fields: return existing, None

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(id)

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
        updated = execute_query(query, tuple(params), fetch=True)
        return updated[0], None
    except Exception as e:
        return None, str(e)
    
def delete_user_db(id: int):
    """Delete a user by id"""
    try:
        deleted_user = execute_query(
            "DELETE FROM users WHERE id = %s RETURNING id, username",
            (id,),
            fetch=True
        )
        if deleted_user:
            return deleted_user[0], None
        return None, "User not found"
    except Exception as e:
        return None, str(e)

def get_user_by_username_db(username: str):
    """Get user by username"""
    try:
        users = execute_query("SELECT * FROM users WHERE username = %s", (username,), fetch=True)
        if users:
            return users[0], None
        return None, "User not found"
    except Exception as e:
        return None, str(e)

def get_users_by_role_db(role: str):
    """Get users by role"""
    try:
        users = execute_query("SELECT * FROM users WHERE role = %s", (role,), fetch=True)
        return users, None if users else "User not found"
    except Exception as e:
        return None, str(e)

def get_user_by_email_db(email: str):
    """Get user by email"""
    try:
        users = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch=True)
        if users:
            return users[0], None
        return None, "User not found"
    except Exception as e:
        return None, str(e)



def get_user_favorite_genre_stats_db(user_id: int):
    """User's favorite genres from collections"""
    try:
        query = """
        SELECT g.genre_name, COUNT(*) as genre_count
        FROM user_lists ul
        JOIN list_items li ON ul.id = li.list_id
        JOIN movies m ON li.movie_id = m.id
        JOIN movies_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE ul.user_id = %s
        GROUP BY g.genre_name
        ORDER BY genre_count DESC LIMIT 5;
        """
        result = execute_query(query, (user_id,), fetch=True)
        return result, None
    except Exception as e:
        return None, str(e)

def get_most_active_curators_db():
    """Users who created the most collections"""
    try:
        query = """
        SELECT u.username, u.profile_picture, COUNT(li.movie_id) as total_movies
        FROM users u
        JOIN user_lists ul ON u.id = ul.user_id
        JOIN list_items li ON ul.id = li.list_id
        GROUP BY u.id, u.username, u.profile_picture
        HAVING COUNT(li.movie_id) > 0
        ORDER BY total_movies DESC LIMIT 5;
        """
        result = execute_query(query, fetch=True)
        return result, None
    except Exception as e:
        return None, str(e)