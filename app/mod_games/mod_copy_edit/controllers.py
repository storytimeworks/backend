from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import admin_required, db
from app.chinese import segment
from app.mod_games import Game
import app.mod_games.mod_copy_edit.errors as errors
from app.mod_games.mod_copy_edit.models import CopyEditQuestion
from app.mod_games.mod_copy_edit.models import CopyEditResult
from app.mod_mastery import update_masteries
from app.mod_passages.models import Passage
from app.mod_vocab.models import Entry
from app.utils import check_body

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
    result = GameResult(current_user.id, Game.COPY_EDIT, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Copy Edit game result
    copy_edit_result = CopyEditResult(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
    db.session.add(copy_edit_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())

@mod_copy_edit_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all Copy Edit questions.

    Parameters:
        q: The query that should be used for the search.

    Returns:
        JSON data for all the questions.
    """

    questions = []

    if "q" in request.args:
        # Use the query to search for questions if one is included
        query = "%" + request.args.get("q") + "%"

        # Ensure the correct questions are being returned
        questions = CopyEditQuestion.query.filter(
            CopyEditQuestion.prompt.like(query) |
            CopyEditQuestion.explanation.like(query) |
            CopyEditQuestion.correct_sentence.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = CopyEditQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_copy_edit_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a Copy Edit question.

    Returns:
        JSON data of the question.
    """

    question = CopyEditQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_copy_edit_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for Copy Edit.

    Body:
        prompt: The sentence that needs to be corrected.
        explanation: The explanation for why the original sentence is wrong.
        correct_sentence: The correct sentence.

    Returns:
        JSON data of this question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompt", "explanation", "correct_sentence"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"]
    explanation = request.json["explanation"]
    correct_sentence = request.json["correct_sentence"]

    # Create the question and store it in MySQL
    question = CopyEditQuestion(prompt, explanation, correct_sentence)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_copy_edit_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a Copy Edit question.Currently only one key can be updated at a
    time.

    Body:
        prompt: The sentence that needs to be corrected.
        explanation: The explanation for why the original sentence is wrong.
        correct_sentence: The correct sentence.

    Returns:
        JSON data of this question.
    """

    key = None
    value = None

    # Try to get the key and value being updated
    if request.json is not None and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_question_parameters()

    # Find the question being updated
    question = CopyEditQuestion.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "prompt":
        question.prompt = value
    elif key == "explanation":
        question.explanation = value
    elif key == "correct_sentence":
        question.correct_sentence = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated quesiton JSON data
    return jsonify(question.serialize())

@mod_copy_edit_game.route("/status", methods=["GET"])
@admin_required
def get_status():
    questions = CopyEditQuestion.query.all()

    # A list of all words seen in all Copy Edit questions
    words = set()

    for question in questions:
        # Get the words in each question
        question_words = [word for word in segment(question.prompt)]

        # Add this question's words to the words set
        words.update(question_words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return json.dumps(list(words), ensure_ascii=False)
