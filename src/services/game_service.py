from src.config.database import execute_query
import random
from src.services.statistic_service import get_statistic_by_id_db

def get_random_question_db(game_types=None):
    """
    Fetches a random question from the database.
    Returns a dictionary with question details and the two movies.
    """
    try:
        # get a random question
        # use ORDER BY RANDOM() LIMIT 1. 
        
        where_clause = ""
        params = []
        if game_types:
            # game_types is a list of strings like ['1', '2']
            placeholders = ', '.join(['%s'] * len(game_types))
            where_clause = f"WHERE mq.question_type IN ({placeholders})"
            params = game_types
            
        query = f"""
            SELECT 
                mq.id as question_id,
                qt.question_type_name,
                m1.id as movie1_id, m1.title as movie1_title, m1.poster_file as movie1_poster,
                m2.id as movie2_id, m2.title as movie2_title, m2.poster_file as movie2_poster
            FROM movie_question mq
            JOIN question_types qt ON mq.question_type = qt.id
            JOIN movies m1 ON mq.movie1_id = m1.id
            JOIN movies m2 ON mq.movie2_id = m2.id
            {where_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        result = execute_query(query, tuple(params) if params else None, fetch=True)
        
        if result:
            return result[0], None
        return None, "No questions found"
    except Exception as e:
        return None, str(e)

def check_answer_db(question_id, selected_movie_id):
    """
    Verifies if the selected movie is the correct answer.
    Returns (is_correct, correct_movie_id, details)
    """
    try:
        # get question details
        row, err = get_question_by_id_db(question_id)
        
        if err or not row:
            return False, None, "Question not found"
            
        movie1_id = row['movie1_id']
        movie2_id = row['movie2_id']
        question_type = row['question_type_name']
        
        # get stats for both movies
        m1_stats, err1 = get_statistic_by_id_db(movie1_id)
        m2_stats, err2 = get_statistic_by_id_db(movie2_id)
        
        if err1 or err2 or not m1_stats or not m2_stats:
             return False, None, "Statistics missing for one or both movies"

        # compare based on question type
        # question_types: higher_budget, higher_revenue, longer_runtime, higher_rating, more_votes
        
        val1 = 0
        val2 = 0
        
        if question_type == 'higher_budget':
            val1 = m1_stats['budget']
            val2 = m2_stats['budget']
        elif question_type == 'higher_revenue':
            val1 = m1_stats['revenue']
            val2 = m2_stats['revenue']
        elif question_type == 'longer_runtime':
            val1 = m1_stats['runtime']
            val2 = m2_stats['runtime']
        elif question_type == 'higher_rating':
            val1 = m1_stats['vote_avg']
            val2 = m2_stats['vote_avg']
        elif question_type == 'more_votes':
            val1 = m1_stats['vote_count']
            val2 = m2_stats['vote_count']
            
        # determine winner
        correct_movie_id = None
        if val1 > val2:
            correct_movie_id = movie1_id
        elif val2 > val1:
            correct_movie_id = movie2_id
        else:
            # tie not happening but for safety 
            correct_movie_id = selected_movie_id 

        is_correct = (str(selected_movie_id) == str(correct_movie_id))
        
        # format values for display
        if question_type in ['higher_budget', 'higher_revenue']:
            val1_fmt = f"${val1:,.0f}"
            val2_fmt = f"${val2:,.0f}"
        elif question_type == 'longer_runtime':
            val1_fmt = f"{val1} min"
            val2_fmt = f"{val2} min"
        elif question_type == 'higher_rating':
            val1_fmt = f"{val1}/10"
            val2_fmt = f"{val2}/10"
        elif question_type == 'more_votes':
            val1_fmt = f"{val1:,} votes"
            val2_fmt = f"{val2:,} votes"
        else:
            val1_fmt = str(val1)
            val2_fmt = str(val2)

        result_details = {
            'movie1_id': movie1_id,
            'movie2_id': movie2_id,
            'movie1_val': val1_fmt,
            'movie2_val': val2_fmt,
            'correct_movie_id': correct_movie_id
        }
        
        return is_correct, correct_movie_id, result_details

    except Exception as e:
        return False, None, str(e)


def get_questions_db():
    """Get all questions"""
    try:
        query = """
            SELECT 
                mq.id,
                mq.question_type,
                qt.question_type_name,
                mq.movie1_id,
                m1.title as movie1_title,
                m1.poster_file as movie1_poster,
                mq.movie2_id,
                m2.title as movie2_title,
                m2.poster_file as movie2_poster
            FROM movie_question mq
            JOIN question_types qt ON mq.question_type = qt.id
            JOIN movies m1 ON mq.movie1_id = m1.id
            JOIN movies m2 ON mq.movie2_id = m2.id
            ORDER BY mq.id
        """
        questions = execute_query(query, fetch=True)
        return questions, None
    except Exception as e:
        return None, str(e)


def get_question_by_id_db(id):
    """Get question by id"""
    try:
        query = """
            SELECT 
                mq.id,
                mq.question_type,
                qt.question_type_name,
                mq.movie1_id,
                m1.title as movie1_title,
                m1.poster_file as movie1_poster,
                mq.movie2_id,
                m2.title as movie2_title,
                m2.poster_file as movie2_poster
            FROM movie_question mq
            JOIN question_types qt ON mq.question_type = qt.id
            JOIN movies m1 ON mq.movie1_id = m1.id
            JOIN movies m2 ON mq.movie2_id = m2.id
            WHERE mq.id = %s
        """
        questions = execute_query(query, (id,), fetch=True)
        if questions:
            return questions[0], None
        return None, "Question not found"
    except Exception as e:
        return None, str(e)


def create_question_db(data):
    """Create a new question"""
    try:
        # make sure for all required fields
        if not all(k in data for k in ('question_type', 'movie1_id', 'movie2_id')):
            return None, "Missing required fields"

        query = """
            INSERT INTO movie_question (question_type, movie1_id, movie2_id)
            VALUES (%s, %s, %s)
            RETURNING id, question_type, movie1_id, movie2_id
        """
        params = (data['question_type'], data['movie1_id'], data['movie2_id'])
        
        new_question = execute_query(query, params, fetch=True)
        if new_question:
            return new_question[0], None
        return None, "Failed to create question"
    except Exception as e:
        return None, str(e)


def update_question_db(id, data):
    """Update a question"""
    try:
        # check if question exists
        existing, err = get_question_by_id_db(id)
        if err:
            return None, err
        if not existing:
            return None, "Question not found"

        update_fields = []
        params = []

        if 'question_type' in data:
            update_fields.append("question_type = %s")
            params.append(data['question_type'])
        if 'movie1_id' in data:
            update_fields.append("movie1_id = %s")
            params.append(data['movie1_id'])
        if 'movie2_id' in data:
            update_fields.append("movie2_id = %s")
            params.append(data['movie2_id'])

        if not update_fields:
            return existing, None

        params.append(id)
        
        query = f"""
            UPDATE movie_question
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, question_type, movie1_id, movie2_id
        """
        
        updated = execute_query(query, tuple(params), fetch=True)
        if updated:
            return updated[0], None
        return None, "Failed to update question"
    except Exception as e:
        return None, str(e)


def delete_question_db(id):
    """Delete a question"""
    try:
        query = "DELETE FROM movie_question WHERE id = %s RETURNING id"
        deleted = execute_query(query, (id,), fetch=True)
        if deleted:
            return deleted[0], None
        return None, "Question not found"
    except Exception as e:
        return None, str(e)


def get_leaderboard_db(limit=50):
    """Get top players by game score"""
    try:
        query = """
            SELECT 
                id, 
                username, 
                game_score as score, 
                profile_picture as avatar, 
                role 
            FROM users 
            WHERE game_score > 0 
            ORDER BY game_score DESC 
            LIMIT %s
        """
        leaderboard = execute_query(query, (limit,), fetch=True)
        # Add rank and other display fields if needed, or handle in template
        # The template expects: user.score, user.best_streak, user.games_played
        # Our DB currently only has game_score. 
        # We can pass what we have.
        return leaderboard, None
    except Exception as e:
        return None, str(e)


def update_user_score_db(user_id, new_score):
    """
    Update user's high score. 
    Only updates if new_score is higher than existing game_score.
    """
    try:
        # First get current score
        query_get = "SELECT game_score FROM users WHERE id = %s"
        current = execute_query(query_get, (user_id,), fetch=True)
        
        if not current:
            return False, "User not found"
            
        current_score = current[0]['game_score']
        if current_score is None: 
            current_score = 0
            
        if new_score > current_score:
            query_update = "UPDATE users SET game_score = %s WHERE id = %s RETURNING game_score"
            updated = execute_query(query_update, (new_score, user_id), fetch=True)
            if updated:
                return True, None
            return False, "Failed to update score"
            
        return False, "Score not higher than best"
        
    except Exception as e:
        return False, str(e)
