from src.config.database import execute_query

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