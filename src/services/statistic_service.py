from src.config.database import execute_query


def get_statistics_paginated_db(page=1, per_page=20):
    """Get all statistics paginated"""
    try:
        from src.utils.pagination_utils import Pagination
        
        offset = (page - 1) * per_page
        
        # count total
        count_query = "SELECT COUNT(*) as count FROM statistic"
        count_res = execute_query(count_query, fetch=True)
        total_count = count_res[0]['count'] if count_res else 0
        
        # get data
        query = """
            SELECT movie_id, budget, revenue, runtime, vote_avg, vote_count
            FROM statistic
            ORDER BY movie_id
            LIMIT %s OFFSET %s
        """
        stats = execute_query(query, (per_page, offset), fetch=True) or []
        
        return Pagination(items=[dict(s) for s in stats],
                          page=page,
                          per_page=per_page,
                          total_count=total_count), None
    except Exception as e:
        return None, str(e)

def get_statistics_db():
    """Get all statistics (Legacy/Non-paginated)"""
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


def get_cinemetrics_movies_db(metric_type: str, page: int = 1, per_page: int = 8):
    """
    Get paginated movies based on specific "Cinemetrics" criteria.
    Types: 'hidden_gems', 'short', 'critics', 'revenue'
    """
    try:
        from src.services.movie_service import Pagination
        
        offset = (page - 1) * per_page
        
        base_query = """
            SELECT m.id, m.title, m.poster_file, m.release_date, 
                   s.vote_avg, s.vote_count, s.runtime, s.revenue
            FROM movies m
            JOIN statistic s ON m.id = s.movie_id
        """
        
        where_clause = ""
        order_clause = ""
        params = []
        
        if metric_type == 'hidden_gems':
            # high rating (>= 7.0) with low-ish vote count (< 1000 but > 50)
            where_clause = "WHERE s.vote_avg >= 7.0 AND s.vote_count BETWEEN 50 AND 1000"
            order_clause = "ORDER BY RANDOM()"
            
        elif metric_type == 'short':
             # runtime < 90 mins
            where_clause = "WHERE s.runtime > 0 AND s.runtime < 90"
            order_clause = "ORDER BY RANDOM()"
            
        elif metric_type == 'critics':
            # very high rating (>= 8.0)
            where_clause = "WHERE s.vote_avg >= 8.0"
            order_clause = "ORDER BY RANDOM()"
            
        elif metric_type == 'revenue':
            # top revenue
            where_clause = "WHERE s.revenue > 0"
            order_clause = "ORDER BY s.revenue DESC"
            
        elif metric_type == 'time_capsule':
            # best movie from every year
            # specific complex handlked different
            pass

        elif metric_type == 'timeless':
            # old movies (pre-2000) with recent comments (last 30 days)
            # needs a join with comments as time_capsule handled differently
            pass

        else:
            return None, "Invalid metric type"

        if metric_type == 'time_capsule':
            # special case for complex window function query
            query = f"""
                SELECT * FROM (
                    SELECT 
                        m.id,
                        m.title,
                        m.poster_file,
                        m.release_date,
                        s.vote_avg,
                        s.vote_count,
                        s.runtime,
                        s.revenue,
                        RANK() OVER (
                            PARTITION BY EXTRACT(YEAR FROM m.release_date) 
                            ORDER BY s.vote_avg DESC, s.vote_count DESC
                        ) as yearly_rank
                    FROM movies m
                    JOIN statistic s ON m.id = s.movie_id
                    WHERE m.release_date IS NOT NULL AND s.vote_count > 100 -- Minimum votes filter for quality
                ) ranked_movies
                WHERE yearly_rank = 1
                ORDER BY release_date DESC
                LIMIT %s OFFSET %s
            """
            params = [per_page, offset]
            movies = execute_query(query, tuple(params), fetch=True) or []
            
            # count for pagination
            count_sql = """
                SELECT COUNT(DISTINCT EXTRACT(YEAR FROM release_date)) as count 
                FROM movies m 
                JOIN statistic s ON m.id = s.movie_id 
                WHERE m.release_date IS NOT NULL AND s.vote_count > 100
            """
            total_res = execute_query(count_sql, fetch=True)
            total_count = total_res[0]['count'] if total_res else 0
            
        elif metric_type == 'timeless':
             # query for timeless trending
            query = f"""
                SELECT m.id, m.title, m.poster_file, m.release_date, 
                       s.vote_avg, s.vote_count, s.runtime, s.revenue,
                       COUNT(c.id) as recent_comments
                FROM movies m
                JOIN statistic s ON m.id = s.movie_id
                LEFT JOIN comments c ON m.id = c.movie_id
                WHERE m.release_date < '2000-01-01' 
                  AND c.created_at >= NOW() - INTERVAL '30 DAYS'
                GROUP BY m.id, s.vote_avg, s.vote_count, s.runtime, s.revenue
                ORDER BY recent_comments DESC
                LIMIT %s OFFSET %s
            """
            params = [per_page, offset]
            movies = execute_query(query, tuple(params), fetch=True) or []
            
            # count for pagination
            count_sql = """
                SELECT COUNT(DISTINCT m.id) as count
                FROM movies m
                JOIN comments c ON m.id = c.movie_id
                WHERE m.release_date < '2000-01-01' 
                  AND c.created_at >= NOW() - INTERVAL '30 DAYS'
            """
            total_res = execute_query(count_sql, fetch=True)
            total_count = total_res[0]['count'] if total_res else 0
            
        else:
            # standard simple queries
            count_sql = f"SELECT COUNT(*) as count FROM movies m JOIN statistic s ON m.id = s.movie_id {where_clause}"
            total_res = execute_query(count_sql, tuple(params), fetch=True)
            total_count = total_res[0]['count'] if total_res else 0

            # data
            data_sql = f"""
                {base_query}
                {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset])
            movies = execute_query(data_sql, tuple(params), fetch=True) or []
        
        # transform to match what templates expect 
        movie_objects = []
        for m in movies:
            movie_objects.append({
                'id': m['id'],
                'title': m['title'],
                'poster_file': m['poster_file'], 
                'release_date': m['release_date'],
                'rating': float(m['vote_avg'] or 0),
                'vote_count': m['vote_count'],
                'runtime': m['runtime']
            })

        return Pagination(items=movie_objects,
                          page=page,
                          per_page=per_page,
                          total_count=total_count), None

    except Exception as e:
        return None, str(e)

def get_platform_share_db():
    """Get platform market share (Top 10 + Others)"""
    try:
        query = """
            SELECT 
                p.platform_name, 
                COUNT(m.id) as movie_count
            FROM platforms p
            JOIN movies m ON p.id = m.platform_id
            GROUP BY p.id, p.platform_name
            ORDER BY movie_count DESC
        """
        all_platforms = execute_query(query, fetch=True)
        if not all_platforms:
            return [], None
            
        # process for Top 10 + Others
        if len(all_platforms) > 10:
            top_10 = all_platforms[:10]
            others_count = sum(p['movie_count'] for p in all_platforms[10:])
            result = [dict(p) for p in top_10]
            result.append({'platform_name': 'Others', 'movie_count': others_count})
            return result, None
            
        return [dict(p) for p in all_platforms], None
    except Exception as e:
        return None, str(e)

def get_genre_popularity_db():
    """Get genre popularity"""
    try:
        query = """
            SELECT 
                g.genre_name,
                COUNT(mg.movie_id) as total_movies
            FROM genres g
            JOIN movies_genres mg ON g.id = mg.genre_id
            GROUP BY g.id, g.genre_name
            ORDER BY total_movies DESC
            LIMIT 8
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)

def get_release_timeline_db():
    """Get movies released per year"""
    try:
        query = """
            SELECT 
                EXTRACT(YEAR FROM release_date) as release_year,
                COUNT(id) as movie_count
            FROM movies
            WHERE release_date IS NOT NULL
            GROUP BY release_year
            ORDER BY release_year ASC
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)

def get_runtime_trend_db():
    """Get average runtime per year"""
    try:
        query = """
            SELECT 
                EXTRACT(YEAR FROM m.release_date) as year,
                ROUND(AVG(s.runtime), 0) as avg_minutes
            FROM movies m
            JOIN statistic s ON m.id = s.movie_id
            WHERE m.release_date IS NOT NULL 
              AND s.runtime > 30 
            GROUP BY year
            ORDER BY year ASC
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)

def get_rating_distribution_db():
    """Get vote average distribution (Bell Curve)"""
    try:
        # grouping
        query = """
            SELECT 
                CASE 
                    WHEN vote_avg < 2 THEN '1-2'
                    WHEN vote_avg >= 2 AND vote_avg < 4 THEN '3-4'
                    WHEN vote_avg >= 4 AND vote_avg < 6 THEN '5-6'
                    WHEN vote_avg >= 6 AND vote_avg < 8 THEN '7-8'
                    ELSE '9-10'
                END as rating_range,
                COUNT(movie_id) as count
            FROM statistic
            WHERE vote_avg IS NOT NULL
            GROUP BY rating_range
            ORDER BY rating_range
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)

def get_seasonal_revenue_db():
    """Get average revenue by month"""
    try:
        query = """
            SELECT 
                EXTRACT(MONTH FROM release_date) as month,
                AVG(s.revenue) as avg_revenue
            FROM movies m
            JOIN statistic s ON m.id = s.movie_id
            WHERE m.release_date IS NOT NULL AND s.revenue > 0
            GROUP BY month
            ORDER BY month ASC
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)

def get_bankable_stars_db():
    """Get top actors by average movie rating (Quality Control)"""
    try:
        query = """
            SELECT 
                p.name, 
                ROUND(AVG(s.vote_avg), 2) as rating_average,
                COUNT(s.movie_id) as movie_count
            FROM people p
            JOIN movie_cast mc ON p.id = mc.person_id
            JOIN statistic s ON mc.movie_id = s.movie_id
            WHERE mc.role = 'Actor'
            GROUP BY p.id, p.name
            HAVING COUNT(s.movie_id) >= 5 
            ORDER BY rating_average DESC
            LIMIT 10
        """
        return execute_query(query, fetch=True), None
    except Exception as e:
        return None, str(e)
