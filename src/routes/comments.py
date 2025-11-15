from flask import Blueprint, jsonify, request
from src.config.database import execute_query

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/', methods=['GET'])
def get_all_comments():
    """Gets all comments"""
    try:
        comments = execute_query(
            """
            SELECT * FROM comments
            ORDER BY created_at DESC
            """,
            fetch=True
        )
        return jsonify([dict(comment) for comment in comments])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    """Gets a single comment by its ID"""
    try:
        comment = execute_query(
            """
            SELECT * FROM comments
            WHERE id = %s
            """,
            (comment_id,),
            fetch=True
        )
        if comment:
            return jsonify(dict(comment[0]))
        return jsonify({'error': 'Comment not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@comments_bp.route('/', methods=['POST'])
def create_comment():
    """Creates a new comment AND updates the movie's average rating"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'movie_id' not in data or 'body' not in data:
            return jsonify({'error': 'user_id, movie_id, and body are required'}), 400
        
        user_id = data['user_id']
        movie_id = data['movie_id']
        body = data['body']
        rating = data.get('rating') 
        comment_likes = data.get('comment_likes', 0)
        comment_dislikes = data.get('comment_dislikes', 0)
        
        new_comment = execute_query(
            """
            INSERT INTO comments (user_id, movie_id, body, rating, comment_likes, comment_dislikes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                user_id,
                movie_id,
                body,
                rating,
                comment_likes,
                comment_dislikes
            ),
            fetch=True
        )
        
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
                print(f"WARNING: Comment {new_comment[0]['id']} created, but failed to update rating statistics for movie {movie_id}. Error: {e}")

        if new_comment:
            return jsonify(dict(new_comment[0])), 201
            
        return jsonify({'error': 'Failed to create comment'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/<int:comment_id>', methods=['PUT', 'PATCH'])
def update_comment(comment_id):
    """Updates an existing comment (usually just the body and rating)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        comment_check = execute_query(
            "SELECT id FROM comments WHERE id = %s",
            (comment_id,),
            fetch=True
        )
        
        if not comment_check:
            return jsonify({'error': 'Comment not found'}), 404
            
        update_fields = []
        params = []
        
        if 'body' in data:
            update_fields.append("body = %s")
            params.append(data['body'])
        if 'rating' in data:
            update_fields.append("rating = %s")
            params.append(data['rating'])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update (body or rating)'}), 400
            
        params.append(comment_id)
        
        query = f"""
            UPDATE comments
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        
        updated_comment = execute_query(
            query,
            tuple(params),
            fetch=True
        )
        
        if updated_comment:
            return jsonify(dict(updated_comment[0]))
            
        return jsonify({'error': 'Failed to update comment'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Deletes a comment"""
    try:
        comment = execute_query(
            "SELECT * FROM comments WHERE id = %s",
            (comment_id,),
            fetch=True
        )
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
            
        execute_query(
            "DELETE FROM comments WHERE id = %s",
            (comment_id,)
        )
        
        return jsonify({
            'message': 'Comment deleted successfully',
            'comment': dict(comment[0])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_comments_for_movie(movie_id):
    """Gets all comments for a specific movie"""
    try:
        comments = execute_query(
            """
            SELECT * FROM comments 
            WHERE movie_id = %s 
            ORDER BY created_at DESC
            """,
            (movie_id,),
            fetch=True
        )
        
        if not comments:
            return jsonify({'message': 'No comments found for this movie'}), 404
            
        return jsonify([dict(comment) for comment in comments])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/movie/<int:movie_id>/best', methods=['GET'])
def get_comments_for_movie_best_first(movie_id):
    """Gets all comments for a movie, sorted by best rating"""
    try:
        comments = execute_query(
            """
            SELECT * FROM comments 
            WHERE movie_id = %s 
            ORDER BY rating DESC, created_at DESC
            """,
            (movie_id,),
            fetch=True
        )
        
        if not comments:
            return jsonify({'message': 'No comments found for this movie'}), 404
            
        return jsonify([dict(comment) for comment in comments])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/movie/<int:movie_id>/worst', methods=['GET'])
def get_comments_for_movie_worst_first(movie_id):
    """Gets all comments for a movie, sorted by worst rating"""
    try:
        comments = execute_query(
            """
            SELECT * FROM comments 
            WHERE movie_id = %s AND rating IS NOT NULL
            ORDER BY rating ASC, created_at DESC
            """,
            (movie_id,),
            fetch=True
        )
        
        if not comments:
            return jsonify({'message': 'No comments found for this movie'}), 404
            
        return jsonify([dict(comment) for comment in comments])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    """Increments the 'comment_likes' count for a comment"""
    try:
        comment_check = execute_query(
            "SELECT id FROM comments WHERE id = %s",
            (comment_id,),
            fetch=True
        )
        
        if not comment_check:
            return jsonify({'error': 'Comment not found'}), 404

        updated_comment = execute_query(
            """
            UPDATE comments 
            SET comment_likes = comment_likes + 1 
            WHERE id = %s 
            RETURNING *
            """,
            (comment_id,),
            fetch=True
        )
        
        if updated_comment:
            return jsonify(dict(updated_comment[0]))
        
        return jsonify({'error': 'Failed to like comment'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@comments_bp.route('/<int:comment_id>/dislike', methods=['POST'])
def dislike_comment(comment_id):
    """Increments the 'comment_dislikes' count for a comment"""
    try:
        comment_check = execute_query(
            "SELECT id FROM comments WHERE id = %s",
            (comment_id,),
            fetch=True
        )
        
        if not comment_check:
            return jsonify({'error': 'Comment not found'}), 404

        updated_comment = execute_query(
            """
            UPDATE comments 
            SET comment_dislikes = comment_dislikes + 1 
            WHERE id = %s 
            RETURNING *
            """,
            (comment_id,),
            fetch=True
        )
        
        if updated_comment:
            return jsonify(dict(updated_comment[0]))
        
        return jsonify({'error': 'Failed to dislike comment'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500