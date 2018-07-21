mod_copy_edit_game = Blueprint("copy_edit_game", __name__, url_prefix="/games/copy_edit")

@mod_copy_edit_game.route("/play", methods=["GET"])
@login_required
def play_game(words=None):
    """Retrieves 5 questions in order to play Copy Edit.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return Copy Edit questions for this user
    questions = CopyEditQuestion.play_game(words)
    return jsonify(questions)

@mod_copy_edit_game.route("/play/passages/<passage_id>", methods=["GET"])
@login_required
def play_game_for_passage(passage_id):
    """Plays Copy Edit according to the contents of a passage.

    Parameters:
        passage_id: The id of the passage to play this game with.

    Returns:
        JSON data of the game data.
    """

    # Retrieve the passage with the id passed to us
    passage = Passage.query.filter_by(id=passage_id).first()

    # Return 404 if the passage doesn't exist
    if passage is None:
        return passage_errors.passage_not_found()

    # Load the passage's new words list and use it to return game data
    words = json.loads(passage.new_words)
    return play_game(words)

@mod_copy_edit_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game and stores any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(request, ["correct", "correct_question_ids", "correct_words", "wrong", "wrong_question_ids", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_question_ids = request.json["correct_question_ids"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_question_ids = request.json["wrong_question_ids"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, 4, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Copy Edit game result
    copy_edit_result = CopyEditResult(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
    db.session.add(copy_edit_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    #  Return the general game result as JSON data
     return jsonify(result.serialize())

@mod_copy_edit_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    questions = CopyEditQuestion.query.all()
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)
