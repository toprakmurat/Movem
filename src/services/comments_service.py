from src.config.database import execute_query


def get_all_comments():
    """Gets all comments"""
    try:
        comments = execute_query("SELECT * FROM comments ORDER BY created_at DESC", fetch=True)
        return comments, None
    except Exception as e:
        return None, str(e)
    
    
def get_comment_by_id(comment_id):
    """Gets a single comment by its ID"""
    try:
        comment = execute_query("SELECT * FROM comments WHERE id = %s", (comment_id,), fetch=True)
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
        rating = comment_data.get('rating') 
        comment_likes = comment_data.get('comment_likes', 0)
        comment_dislikes = comment_data.get('comment_dislikes', 0)

        new_comment_list = execute_query(
            """
            INSERT INTO comments (user_id, movie_id, body, rating, comment_likes, comment_dislikes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (user_id, movie_id, body, rating, comment_likes, comment_dislikes),
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
    """Updates an existing comment AND recalculates the movie's average rating"""
    try:
        comment_check, err = get_comment_by_id(comment_id)
        if err:
            return None, err
        
        old_rating = comment_check.get('rating')
        movie_id = comment_check.get('movie_id') 

        update_fields = []
        params = []
        
        if 'body' in comment_data:
            update_fields.append("body = %s")
            params.append(comment_data['body'])
        if 'rating' in comment_data:
            update_fields.append("rating = %s")
            params.append(comment_data['rating'])
        
        if not update_fields:
            return comment_check, None 

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
                        vote_avg = ( (COALESCE(vote_avg, 0) * COALESCE(vote_count, 0)) - COALESCE(%s, 0) + %s ) / COALESCE(vote_count, 1)
                    WHERE movie_id = %s
                    """,
                    (old_rating, new_rating, movie_id)
                )
            except Exception as e:
                print(f"WARNING: Comment {comment_id} updated, but failed to *recalculate* statistics for movie {movie_id}. Error: {e}")

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


def get_comments_for_movie(movie_id):
    """Gets all comments for a specific movie"""
    try:
        comments = execute_query(
            "SELECT * FROM comments WHERE movie_id = %s ORDER BY created_at DESC",
            (movie_id,), fetch=True
        )
        if comments:
            return comments, None
        return None, "No comments found for this movie"
    except Exception as e:
        return None, str(e)


def get_comments_for_movie_sorted(movie_id, sort_order="DESC"):
    """Gets all comments for a movie, sorted by rating"""
    if sort_order.upper() not in ["ASC", "DESC"]:
        sort_order = "DESC"
        
    try:
        comments = execute_query(
            f"""
            SELECT * FROM comments 
            WHERE movie_id = %s AND rating IS NOT NULL
            ORDER BY rating {sort_order}, created_at DESC
            """,
            (movie_id,), fetch=True
        )
        if comments:
            return comments, None
        return None, "No rated comments found for this movie"
    except Exception as e:
        return None, str(e)


def like_comment(comment_id):
    """Increments the 'comment_likes' count"""
    try:
        updated = execute_query(
            "UPDATE comments SET comment_likes = comment_likes + 1 WHERE id = %s RETURNING *",
            (comment_id,), fetch=True
        )
        if updated:
            return updated[0], None
        return None, "Comment not found"
    except Exception as e:
        return None, str(e)


def dislike_comment(comment_id):
    """Increments the 'comment_dislikes' count"""
    try:
        updated = execute_query(
            "UPDATE comments SET comment_dislikes = comment_dislikes + 1 WHERE id = %s RETURNING *",
            (comment_id,), fetch=True
        )
        if updated:
            return updated[0], None
        return None, "Comment not found"
    except Exception as e:
        return None, str(e)