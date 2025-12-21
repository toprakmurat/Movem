from src.config.database import execute_query


def get_all_comments():
    """Gets all comments"""
    try:
        comments = execute_query("SELECT * FROM comments ORDER BY created_at DESC", fetch=True)
        return comments, None
    except Exception as e:
        return None, str(e)
    
    
def get_comment_by_id(comment_id):
    """Gets a single comment by its ID with LIVE vote counts (3NF Fix)"""
    try:
        query = """
            SELECT 
                c.*,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'like') as comment_likes,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'dislike') as comment_dislikes
            FROM comments c 
            WHERE c.id = %s
        """
        comment = execute_query(query, (comment_id,), fetch=True)
        
        if comment:
            return comment[0], None
        return None, "Comment not found"
    except Exception as e:
        return None, str(e)
    
    
def create_comment(comment_data):
    """Creates a new comment AND updates the movie's average rating"""
    try:
        user_id = comment_data.get('user_id')
        movie_id = comment_data.get('movie_id')        
        body = comment_data.get('body')
        if body == "": 
            body = None
        rating = comment_data.get('rating') 
        if rating is None:
            return None, "Rating is required"

        has_spoiler = comment_data.get('has_spoiler', False)

        new_comment_list = execute_query(
            """
            INSERT INTO comments (user_id, movie_id, body, rating, has_spoiler)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (user_id, movie_id, body, rating, has_spoiler),
            fetch=True
        )
        
        if not new_comment_list:
            return None, "Failed to create comment"

        new_comment = new_comment_list[0]

        if rating is not None:
            try:
                execute_query(
                    """
                    UPDATE statistic
                    SET 
                        vote_count = COALESCE(vote_count, 0) + 1,
                        vote_avg = ( (COALESCE(vote_avg, 0) * COALESCE(vote_count, 0)) + %s ) / (COALESCE(vote_count, 0) + 1)
                    WHERE movie_id = %s
                    """,
                    (rating, movie_id)
                )
            except Exception as e:
                print(f"WARNING: Comment {new_comment['id']} created, but failed to update rating statistics for movie {movie_id}. Error: {e}")

        return new_comment, None
    except Exception as e:
        return None, str(e)
    

def update_comment(comment_id, comment_data):
    """Updates an existing comment (body, rating, spoiler) AND recalculates stats"""
    try:
        comment_check, err = get_comment_by_id(comment_id)
        if err:
            return None, err
        
        old_rating = comment_check.get('rating')
        movie_id = comment_check.get('movie_id') 

        update_fields = []
        params = []
                
        if 'body' in comment_data:
            body_val = comment_data['body']
            if body_val == "": 
                body_val = None
            update_fields.append("body = %s")
            params.append(body_val)
        if 'rating' in comment_data:
            if comment_data['rating'] is not None:
                update_fields.append("rating = %s")
                params.append(comment_data['rating'])
        
        if 'has_spoiler' in comment_data:
            update_fields.append("has_spoiler = %s")
            spoiler_val = comment_data['has_spoiler']
            is_spoiler = True if spoiler_val in [True, 'true', 'on', '1'] else False
            params.append(is_spoiler)
        
        if not update_fields:
            return comment_check, None

        update_fields.append("updated_at = NOW()")
        params.append(comment_id)

        query = f"""
            UPDATE comments
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        updated_comment_list = execute_query(query, tuple(params), fetch=True)
        if not updated_comment_list:
            return None, "Failed to update comment"

        updated_comment = updated_comment_list[0]

        new_rating = comment_data.get('rating') 
        if new_rating is not None and new_rating != old_rating:
            try:
                execute_query(
                    """
                    UPDATE statistic
                    SET 
                        vote_avg = ( (COALESCE(vote_avg, 0) * COALESCE(vote_count, 0)) 
                                     - COALESCE(%s, 0) + %s ) 
                                    / COALESCE(vote_count, 1)
                    WHERE movie_id = %s
                    """,
                    (old_rating, new_rating, movie_id)
                )
            except Exception as e:
                print(f"WARNING: Stats update failed: {e}")

        return updated_comment, None
    except Exception as e:
        return None, str(e)
    
    
def delete_comment_by_id(comment_id):
    """Deletes a comment AND updates the movie's average rating"""
    try:
        comment, err = get_comment_by_id(comment_id)
        if err:
            return None, err
        
        rating = comment.get('rating')
        movie_id = comment.get('movie_id')

        deleted = execute_query("DELETE FROM comments WHERE id = %s RETURNING *", (comment_id,), fetch=True)
        
        if not deleted:
            return None, "Comment not found to delete"
        
        if rating is not None:
            try:
                execute_query(
                    """
                    UPDATE statistic
                    SET 
                        vote_count = COALESCE(vote_count, 1) - 1,
                        vote_avg = CASE 
                                    WHEN (COALESCE(vote_count, 1) - 1) > 0 
                                    THEN ( (COALESCE(vote_avg, 0) * COALESCE(vote_count, 1)) - %s ) / (COALESCE(vote_count, 1) - 1)
                                    ELSE 0
                                   END
                    WHERE movie_id = %s
                    """,
                    (rating, movie_id)
                )
            except Exception as e:
                print(f"WARNING: Comment {comment_id} deleted, but failed to update rating statistics. Error: {e}")
        
        return deleted[0], None
    except Exception as e:
        return None, str(e)


def get_comments_for_movie(movie_id, sort_by='newest', spoiler_filter='all', user_id=None):
    """
    Gets comments with filtering, sorting AND username (JOIN).
    3NF DEĞİŞİKLİĞİ: Like ve Dislike sayıları comment_votes tablosundan CANLI sayılıyor.
    """
    try:
        query = """
            SELECT 
                c.*, 
                u.username as author, 
                u.profile_picture as avatar,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'like') as comment_likes,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'dislike') as comment_dislikes
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.movie_id = %s
        """
        params = [movie_id]

        if spoiler_filter == 'hide':
            query += " AND c.has_spoiler = FALSE"

        if sort_by == 'newest':
            query += " ORDER BY c.created_at DESC"
        elif sort_by == 'oldest':
            query += " ORDER BY c.created_at ASC"
        elif sort_by == 'rating_desc':
            query += " ORDER BY c.rating DESC"
        elif sort_by == 'rating_asc':
            query += " ORDER BY c.rating ASC"
        elif sort_by == 'likes':
            query += " ORDER BY comment_likes DESC"
        else:
            query += " ORDER BY c.created_at DESC"

        comments = execute_query(query, tuple(params), fetch=True)
        
        if comments:
            if user_id:
                for comment in comments:
                    vote_type = get_user_vote_status(user_id, comment['id'])
                    comment['user_vote'] = vote_type
            else:
                for comment in comments:
                    comment['user_vote'] = None

            return comments, None
        return [], None

    except Exception as e:
        return None, str(e)


def get_comments_for_movie_sorted(movie_id, sort_order="DESC"):
    """Gets all comments for a movie, sorted by rating, WITH LIVE VOTE COUNTS"""
    if sort_order.upper() not in ["ASC", "DESC"]:
        sort_order = "DESC"
        
    try:

        query = f"""
            SELECT 
                c.*,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'like') as comment_likes,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'dislike') as comment_dislikes
            FROM comments c 
            WHERE c.movie_id = %s AND c.rating IS NOT NULL
            ORDER BY c.rating {sort_order}, c.created_at DESC
        """
        
        comments = execute_query(query, (movie_id,), fetch=True)
        
        if comments:
            return comments, None
        return None, "No rated comments found for this movie"
    except Exception as e:
        return None, str(e)


def like_comment(comment_id):
    """
    DEPRECATED in 3NF: This function updates 'comment_likes' column which no longer exists.
    Use 'toggle_comment_vote_db' instead.
    """
    return None, "This method is deprecated in 3NF structure."


def dislike_comment(comment_id):
    """
    DEPRECATED in 3NF: This function updates 'comment_dislikes' column which no longer exists.
    Use 'toggle_comment_vote_db' instead.
    """
    return None, "This method is deprecated in 3NF structure."
    

def get_comments_by_user(user_id):
    """Get all reviews/ratings made by a specific user."""
    try:
        query = """
            SELECT 
                c.*, 
                m.title as movie_title, 
                m.poster_file as movie_poster,
                m.id as movie_id,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'like') as comment_likes,
                (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'dislike') as comment_dislikes
            FROM comments c
            JOIN movies m ON c.movie_id = m.id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """
        user_reviews = execute_query(query, (user_id,), fetch=True)
        
        if user_reviews:
            return user_reviews, None
        return [], None
    except Exception as e:
        return None, str(e)
    

def get_top_reviewers(limit: int = 10):
    try:
        query = """
            SELECT
                u.username,
                u.profile_picture,
                u.id AS user_id,
                COUNT(c.id) AS review_count
            FROM comments c
            JOIN users u ON c.user_id = u.id
            GROUP BY u.username, u.profile_picture, u.id
            ORDER BY review_count DESC
            LIMIT %s;
        """
        top_reviewers = execute_query(query, (limit,), fetch=True)
        return top_reviewers, None
    except Exception as e:
        return None, str(e)

# COMMENT VOTES SERVICES 

def toggle_comment_vote_db(user_id, comment_id, vote_type='like'):
    """
    Toggles a vote. 3NF VERSION: Updates ONLY comment_votes table.
    """
    try:
        check_query = "SELECT vote_type FROM comment_votes WHERE user_id = %s AND comment_id = %s"
        existing_vote = execute_query(check_query, (user_id, comment_id), fetch=True)
        
        if existing_vote:
            current_type = existing_vote[0]['vote_type']
            
            if current_type == vote_type:
                execute_query("DELETE FROM comment_votes WHERE user_id = %s AND comment_id = %s", (user_id, comment_id))
                return {"action": "removed", "type": vote_type}, None
            else:
                execute_query("UPDATE comment_votes SET vote_type = %s WHERE user_id = %s AND comment_id = %s", (vote_type, user_id, comment_id))
                return {"action": "changed", "type": vote_type}, None
        else:
            execute_query("INSERT INTO comment_votes (user_id, comment_id, vote_type) VALUES (%s, %s, %s)", (user_id, comment_id, vote_type))
            return {"action": "added", "type": vote_type}, None
    except Exception as e:
        return None, str(e)
    

def get_user_vote_status(user_id, comment_id):
    try:
        query = "SELECT vote_type FROM comment_votes WHERE user_id = %s AND comment_id = %s"
        result = execute_query(query, (user_id, comment_id), fetch=True)
        if result:
            return result[0]['vote_type']
        return None
    except Exception as e:
        return None
        

def create_vote(user_id, comment_id, vote_type):
    """
    Creates a new vote record in comment_votes table.
    3NF VERSION: Does NOT update comments table stats.
    """
    try:
        query = """
            INSERT INTO comment_votes (user_id, comment_id, vote_type)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        new_vote = execute_query(query, (user_id, comment_id, vote_type), fetch=True)
        
        if not new_vote:
            return None, "Failed to create vote record"
        return new_vote[0], None

    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return None, "User has already voted on this comment"
        return None, str(e)


def get_vote_by_user_and_comment(user_id, comment_id):
    """Gets a vote record based on user_id and comment_id pair"""
    try:
        query = "SELECT * FROM comment_votes WHERE user_id = %s AND comment_id = %s"
        vote = execute_query(query, (user_id, comment_id), fetch=True)
        
        if vote:
            return vote[0], None
        return None, "Vote not found"
    except Exception as e:
        return None, str(e)


def get_all_votes_for_comment(comment_id):
    """Fetches all votes associated with a specific comment"""
    try:
        query = "SELECT * FROM comment_votes WHERE comment_id = %s"
        votes = execute_query(query, (comment_id,), fetch=True)
        return votes, None
    except Exception as e:
        return None, str(e)


def update_vote(user_id, comment_id, new_vote_type):
    """
    Updates the vote type.
    3NF VERSION: Updates only comment_votes.
    """
    try:
        current_vote, err = get_vote_by_user_and_comment(user_id, comment_id)
        if err:
            return None, err
        
        old_type = current_vote['vote_type']

        if old_type == new_vote_type:
            return current_vote, None

        update_query = """
            UPDATE comment_votes 
            SET vote_type = %s, created_at = NOW() 
            WHERE user_id = %s AND comment_id = %s
            RETURNING *
        """
        updated_vote = execute_query(update_query, (new_vote_type, user_id, comment_id), fetch=True)

        if not updated_vote:
            return None, "Failed to update vote"
        return updated_vote[0], None

    except Exception as e:
        return None, str(e)


def delete_vote(user_id, comment_id):
    """
    Deletes a vote record.
    3NF VERSION: Updates only comment_votes.
    """
    try:
        vote_to_delete, err = get_vote_by_user_and_comment(user_id, comment_id)
        if err:
            return None, err

        delete_query = "DELETE FROM comment_votes WHERE user_id = %s AND comment_id = %s RETURNING *"
        deleted_vote = execute_query(delete_query, (user_id, comment_id), fetch=True)

        if not deleted_vote:
            return None, "Failed to delete vote"
        return deleted_vote[0], None

    except Exception as e:
        return None, str(e)
    

def get_controversial_movies():
    try:
        query = """
            SELECT 
                m.id AS movie_id,
                m.title,
                m.poster_file,
                g.genre_name,
                COUNT(DISTINCT c.id) AS total_comments,
                ROUND(AVG(c.rating), 1) AS avg_rating,
                ROUND(VAR_POP(c.rating), 2) AS polarization_score,
                (
                    SELECT COUNT(*) 
                    FROM comment_votes cv
                    JOIN comments c2 ON cv.comment_id = c2.id
                    WHERE c2.movie_id = m.id
                ) AS community_tension
            FROM 
                movies m
            LEFT JOIN 
                statistic s ON m.id = s.movie_id
            LEFT JOIN 
                comments c ON m.id = c.movie_id            
            JOIN 
                movies_genres mg ON m.id = mg.movie_id
            JOIN 
                genres g ON mg.genre_id = g.id
            WHERE 
                s.revenue > (SELECT AVG(revenue) FROM statistic WHERE revenue > 0)
                AND g.id = (
                    SELECT MIN(genre_id) 
                    FROM movies_genres 
                    WHERE movie_id = m.id
                )
            GROUP BY 
                m.id, m.title, m.poster_file, g.genre_name
            HAVING 
                COUNT(DISTINCT c.id) >= 5 
                AND VAR_POP(c.rating) > 4
            ORDER BY 
                community_tension DESC, polarization_score DESC
            LIMIT 6;
        """
        results = execute_query(query, fetch=True)
        return results, None
    except Exception as e:
        return None, str(e)
    

def get_all_comments_detailed(page=1, per_page=20, search_query=None):
    offset = (page - 1) * per_page
    params = []
    
    sql = """
        SELECT c.*, u.username, m.title as movie_title,
        (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'like') as comment_likes,
        (SELECT COUNT(*) FROM comment_votes v WHERE v.comment_id = c.id AND v.vote_type = 'dislike') as comment_dislikes 
        FROM comments c
        JOIN users u ON c.user_id = u.id
        JOIN movies m ON c.movie_id = m.id
    """
    
    if search_query:
        sql += """ WHERE CAST(c.id AS TEXT) ILIKE %s 
                   OR u.username ILIKE %s 
                   OR m.title ILIKE %s """
        search_term = f"%{search_query}%"
        params.extend([search_term, search_term, search_term])
        
    sql += " ORDER BY c.created_at DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    comments = execute_query(sql, tuple(params), fetch=True)
    
    count_sql = "SELECT COUNT(*) FROM comments c JOIN users u ON c.user_id = u.id JOIN movies m ON c.movie_id = m.id"
    if search_query:
        count_sql += " WHERE CAST(c.id AS TEXT) ILIKE %s OR u.username ILIKE %s OR m.title ILIKE %s"
        total = execute_query(count_sql, tuple(params[:3]), fetch=True)[0]['count']
    else:
        total = execute_query(count_sql, fetch=True)[0]['count']
        
    return comments, total

def get_all_votes_detailed(page=1, per_page=20):
    offset = (page - 1) * per_page
    
    sql = """
        SELECT v.*, u.username, left(c.body, 50) as comment_snippet
        FROM comment_votes v
        JOIN users u ON v.user_id = u.id
        JOIN comments c ON v.comment_id = c.id
        ORDER BY v.created_at DESC 
        LIMIT %s OFFSET %s
    """
    votes = execute_query(sql, (per_page, offset), fetch=True)
    total = execute_query("SELECT COUNT(*) FROM comment_votes", fetch=True)[0]['count']
    
    return votes, total

def toggle_spoiler_status(comment_id):
    try:
        curr = execute_query("SELECT has_spoiler FROM comments WHERE id = %s", (comment_id,), fetch=True)
        if not curr: return False, "Comment not found"
        
        new_status = not curr[0]['has_spoiler']
        
        execute_query(
            "UPDATE comments SET has_spoiler = %s WHERE id = %s",
            (new_status, comment_id)
        )
        return True, None
    except Exception as e:
        return False, str(e)