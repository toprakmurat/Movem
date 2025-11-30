from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from src.services.game_service import get_random_question_db, check_answer_db

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def lobby():
    return render_template('lobby.html')

@game_bp.route('/start', methods=['POST'])
def start_game():
    session['score'] = 0
    session['game_over'] = False
    
    # get selected game types from the form
    game_types = request.form.getlist('game_types')

    # if no types selected, default to all 
    if not game_types:
        game_types = ['1', '2', '3', '4', '5']
        
    session['game_types'] = game_types
    
    return redirect(url_for('game.play'))

@game_bp.route('/play')
def play():
    # if game_over flag is set, render game over state directly or redirect
    if session.get('game_over'):
        return render_template('game.html', game_over=True, score=session.get('score', 0))
        
    if 'score' not in session:
        session['score'] = 0

    game_types = session.get('game_types')
    question, err = get_random_question_db(game_types)
    
    if err:
        flash(f"Error loading question: {err}", "error")
        return redirect(url_for('game.lobby'))
    
    return render_template('game.html', question=question, score=session.get('score', 0))

@game_bp.route('/answer', methods=['POST'])
def answer():
    question_id = request.form.get('question_id')
    selected_movie_id = request.form.get('selected_movie_id')
    
    if not question_id or not selected_movie_id:
        flash("Invalid submission", "error")
        return redirect(url_for('game.play'))
    
    # check_answer_db now returns result_details as the third value
    is_correct, correct_movie_id, result_details = check_answer_db(question_id, selected_movie_id)
    
    # if result_details is a string, it's an error message
    if isinstance(result_details, str):
        flash(f"Error checking answer: {result_details}", "error")
        return redirect(url_for('game.play'))
        
    if is_correct:
        session['score'] = session.get('score', 0) + 100
        # flash("Correct!", "success") 
        # Don't flash, just show result
    else:
        session['game_over'] = True
        

    # to keep it clean fetch the question again by ID
    
    from src.services.game_service import execute_query
    q_query = """
        SELECT 
            mq.id as question_id,
            qt.question_type_name,
            m1.id as movie1_id, m1.title as movie1_title, m1.poster_file as movie1_poster,
            m2.id as movie2_id, m2.title as movie2_title, m2.poster_file as movie2_poster
        FROM movie_question mq
        JOIN question_types qt ON mq.question_type = qt.id
        JOIN movies m1 ON mq.movie1_id = m1.id
        JOIN movies m2 ON mq.movie2_id = m2.id
        WHERE mq.id = %s
    """
    q_result = execute_query(q_query, (question_id,), fetch=True)
    question = q_result[0] if q_result else None

    return render_template('game.html', 
                           question=question, 
                           score=session.get('score', 0),
                           result=result_details,
                           user_selection=int(selected_movie_id),
                           game_over=session.get('game_over', False))
