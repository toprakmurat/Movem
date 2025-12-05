from src.config.database import execute_query

def get_statistics_db():
    """Get all statistics"""
    try:
        query = """
            SELECT movie_id, budget, revenue, runtime, vote_avg, vote_count
            FROM statistic
            ORDER BY movie_id
        """
        stats = execute_query(query, fetch=True)
        return stats, None
    except Exception as e:
        return None, str(e)

def get_statistic_by_id_db(movie_id):
    """Get statistic by movie_id"""
    try:
        query = """
            SELECT movie_id, budget, revenue, runtime, vote_avg, vote_count
            FROM statistic
            WHERE movie_id = %s
        """
        stats = execute_query(query, (movie_id,), fetch=True)
        if stats:
            return stats[0], None
        return None, "Statistic not found"
    except Exception as e:
        return None, str(e)

def create_statistic_db(data):
    """Create a new statistic"""
    try:
        if 'movie_id' not in data:
            return None, "movie_id is required"

        query = """
            INSERT INTO statistic (movie_id, budget, revenue, runtime, vote_avg, vote_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING movie_id, budget, revenue, runtime, vote_avg, vote_count
        """
        params = (
            data.get('movie_id'),
            data.get('budget'),
            data.get('revenue'),
            data.get('runtime'),
            data.get('vote_avg'),
            data.get('vote_count')
        )
        
        new_stat = execute_query(query, params, fetch=True)
        if new_stat:
            return new_stat[0], None
        return None, "Failed to create statistic"
    except Exception as e:
        return None, str(e)

def update_statistic_db(movie_id, data):
    """Update a statistic"""
    try:
        existing, err = get_statistic_by_id_db(movie_id)
        if err:
            return None, err
        if not existing:
            return None, "Statistic not found"

        update_fields = []
        params = []

        for key in ['budget', 'revenue', 'runtime', 'vote_avg', 'vote_count']:
            if key in data:
                update_fields.append(f"{key} = %s")
                params.append(data[key])

        if not update_fields:
            return existing, None

        params.append(movie_id)
        
        query = f"""
            UPDATE statistic
            SET {', '.join(update_fields)}
            WHERE movie_id = %s
            RETURNING movie_id, budget, revenue, runtime, vote_avg, vote_count
        """
        
        updated = execute_query(query, tuple(params), fetch=True)
        if updated:
            return updated[0], None
        return None, "Failed to update statistic"
    except Exception as e:
        return None, str(e)

def delete_statistic_db(movie_id):
    """Delete a statistic"""
    try:
        query = "DELETE FROM statistic WHERE movie_id = %s RETURNING movie_id"
        deleted = execute_query(query, (movie_id,), fetch=True)
        if deleted:
            return deleted[0], None
        return None, "Statistic not found"
    except Exception as e:
        return None, str(e)
