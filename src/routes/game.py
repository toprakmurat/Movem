from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from src.services.game_service import (
    get_random_question_db, 
    check_answer_db,
    get_questions_db,
    get_question_by_id_db,
    create_question_db,
    update_question_db,
    delete_question_db,
    get_leaderboard_db,
    update_user_score_db,
    get_question_types_db,
    create_question_type_db,
    update_question_type_db,
    delete_question_type_db
)
from flask_login import current_user
from src.utils.decorators import admin_required

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def lobby():
    # fetch top 10 for sidebar
    leaderboard_data, err = get_leaderboard_db(limit=10)
    
    # process for template
    processed_leaderboard = []
    if leaderboard_data:
        for user in leaderboard_data:
            processed_leaderboard.append({
                'username': user.get('username'),
                'avatar': user.get('avatar'),
                'score': user.get('score', 0)
            })

    return render_template('lobby.html', leaderboard=processed_leaderboard)

@game_bp.route('/leaderboard')
def leaderboard():
    leaderboard_data, err = get_leaderboard_db()
    if err:
        flash(f"Error loading leaderboard: {err}", "error")
        leaderboard_data = []
    
    processed_leaderboard = []
    if leaderboard_data:
        for user in leaderboard_data:
            processed_leaderboard.append({
                'username': user.get('username'),
                'avatar': user.get('avatar'),
                'score': user.get('score', 0),
                'country': None
            })
            
    return render_template('leaderboard.html', leaderboard=processed_leaderboard)

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
    
    # check_answer_db 
    is_correct, correct_movie_id, result_details = check_answer_db(question_id, selected_movie_id)
    
    # if result_details is a string, it's an error message
    if isinstance(result_details, str):
        flash(f"Error checking answer: {result_details}", "error")
        return redirect(url_for('game.play'))
        
    if is_correct:
        session['score'] = session.get('score', 0) + 100
    else:
        session['game_over'] = True
        # Update user high score if logged in
        if current_user.is_authenticated:
            final_score = session.get('score', 0)
            updated, msg = update_user_score_db(current_user.id, final_score)
            if updated:
                flash("New High Score!", "success")
        
    #fetch the question again by ID
    question, _ = get_question_by_id_db(question_id)

    return render_template('game.html', 
                           question=question, 
                           score=session.get('score', 0),
                           result=result_details,
                           user_selection=int(selected_movie_id),
                           game_over=session.get('game_over', False))


@game_bp.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions"""
    questions, err = get_questions_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify({"items": [dict(q) for q in questions]}), 200


@game_bp.route('/questions/<int:id>', methods=['GET'])
def get_question(id):
    """Get question by id"""
    question, err = get_question_by_id_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not question:
        return jsonify({"message": "Question not found"}), 404
    return jsonify(dict(question)), 200


@game_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    """Create a new question"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    new_question, err = create_question_db(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_question)), 201


@game_bp.route('/questions/<int:id>', methods=['PUT'])
@admin_required
def update_question(id):
    """Update question"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    updated, err = update_question_db(id, data)
    if err:
        return jsonify({"error": err}), 400
    if not updated:
        return jsonify({"message": "Question not found"}), 404
    return jsonify(dict(updated)), 200


@game_bp.route('/questions/<int:id>', methods=['DELETE'])
@admin_required
def delete_question(id):
    """Delete question"""
    deleted, err = delete_question_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted:
        return jsonify({"message": "Question not found"}), 404
    return jsonify(dict(deleted)), 200


@game_bp.route('/question-types', methods=['GET'])
def get_question_types():
    """Get all question types"""
    types, err = get_question_types_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify({"items": [dict(t) for t in types]}), 200


@game_bp.route('/question-types', methods=['POST'])
@admin_required
def create_question_type():
    """Create a question type"""
    data = request.get_json()
    if not data or 'question_type_name' not in data:
        return jsonify({"error": "Missing question_type_name"}), 400
        
    new_type, err = create_question_type_db(data['question_type_name'])
    if err:
        return jsonify({"error": err}), 500
    return jsonify(dict(new_type)), 201


@game_bp.route('/question-types/<int:id>', methods=['PUT'])
@admin_required
def update_question_type(id):
    """Update a question type"""
    data = request.get_json()
    if not data or 'question_type_name' not in data:
        return jsonify({"error": "Missing question_type_name"}), 400
        
    updated, err = update_question_type_db(id, data['question_type_name'])
    if err:
        return jsonify({"error": err}), 500
    if not updated:
        return jsonify({"message": "Not found"}), 404
    return jsonify(dict(updated)), 200


@game_bp.route('/question-types/<int:id>', methods=['DELETE'])
@admin_required
def delete_question_type(id):
    """Delete a question type"""
    deleted, err = delete_question_type_db(id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted:
        return jsonify({"message": "Not found"}), 404
    return jsonify(dict(deleted)), 200
