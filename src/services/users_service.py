from src.config.database import execute_query

def get_users_db():
    """Get all users"""
    try:
        users = execute_query(
            """
            SELECT * FROM users
            """,
            fetch=True
        )
        return users, None
    except Exception as e:
        return None, str(e)

def get_user_by_id_db(id: int):
    """Get user by id"""
    try:
        users = execute_query(
            """
            SELECT *  FROM users
            WHERE id = %s
            """,
            (id,),
            fetch=True
        )
        if users:
            return users[0], None
        return None, "User not found"
    except Exception as e:
        return None, str(e)

def create_user_db(user_data: dict):
    """Create a new user"""
    try:
        new_user = execute_query(
            """
            INSERT INTO users(username, email, birth_date, password_hash, role, game_score)
            VALUES(%s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, birth_date, password_hash, role, created_at
            """,
            (
                user_data.get('username'),
                user_data.get('email'),
                user_data.get('birth_date'),
                user_data.get('password_hash'),
                user_data.get('role'),
                user_data.get('game_score')
            ),
            fetch=True
        )

        if new_user:
            return new_user[0], None
        return None, "Failed to create user"
    except Exception as e:
        return None, str(e)


def update_user_db(id: int, user_data: dict):
    """Update the user with given id and return updated one"""
    try:
        existing_user, err = get_user_by_id(id)
        if err:
            return None, err
        if not existing_user:
            return None, "User not found"

        update_fields = []
        params = []

        allowed_fields = ['username', 'email', 'birth_date', 'password_hash', 'role', 'game_score']

        for key in allowed_fields:
            if key in user_data:
                update_fields.append(f"{key} = %s")
                params.append(user_data[key])

        if not update_fields:
            return existing_user, None

        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        params.append(id)

        updated_user = execute_query(
            f"""
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, username, email, birth_date, password_hash, role, created_at, updated_at, game_score
            """,
            tuple(params),
            fetch=True
        )

        return updated_user[0], None

    except Exception as e:
        return None, str(e)



def delete_user_db(id: int):
    """Delete a user by id"""
    try:
        deleted_user = execute_query(
            """
            DELETE FROM users
            WHERE id = %s
            RETURNING id, username, email, birth_date, password_hash, role, created_at, updated_at
            """,
            (id,),
            fetch=True
        )

        if deleted_user:
            return deleted_user[0], None
        return None, "User not found"

    except Exception as e:
        return None, str(e)
