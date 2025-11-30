from src.config.database import execute_query
import random

def get_random_question_db(game_types=None):
    """
    Fetches a random question from the database.
    Returns a dictionary with question details and the two movies.
    """
    try:
        # Get a random question
        # We use ORDER BY RANDOM() LIMIT 1. Note: efficient enough for small datasets.
        
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
        # 1. Get question details
        q_query = """
            SELECT mq.movie1_id, mq.movie2_id, qt.question_type_name
            FROM movie_question mq
            JOIN question_types qt ON mq.question_type = qt.id
            WHERE mq.id = %s
        """
        q_result = execute_query(q_query, (question_id,), fetch=True)
        
        if not q_result:
            return False, None, "Question not found"
            
        row = q_result[0]
        movie1_id = row['movie1_id']
        movie2_id = row['movie2_id']
        question_type = row['question_type_name']
        
        # 2. Get stats for both movies
        s_query = """
            SELECT movie_id, budget, revenue, runtime, vote_avg, vote_count
            FROM statistic
            WHERE movie_id IN (%s, %s)
        """
        stats = execute_query(s_query, (movie1_id, movie2_id), fetch=True)
        
        if not stats or len(stats) < 2:
             return False, None, "Statistics missing for one or both movies"

        # Map stats by movie_id for easy access
        stats_map = {row['movie_id']: row for row in stats}
        
        m1_stats = stats_map.get(movie1_id)
        m2_stats = stats_map.get(movie2_id)
        
        # 3. Compare based on question type
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
            
        # Determine winner
        correct_movie_id = None
        if val1 > val2:
            correct_movie_id = movie1_id
        elif val2 > val1:
            correct_movie_id = movie2_id
        else:
            # Tie.
            correct_movie_id = selected_movie_id 

        is_correct = (str(selected_movie_id) == str(correct_movie_id))
        
        # Format values for display
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
