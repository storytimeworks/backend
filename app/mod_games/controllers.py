from flask import Blueprint, abort, g, jsonify, request
from flask_login import current_user, login_required
import inspect, json, random

from app import admin_required, db
from app.mod_games import Game
from app.mod_games import GameResult
import app.mod_games.errors as errors
from app.mod_games import Attempt
from app.mod_mastery import update_masteries
import app.mod_passages.errors as passage_errors
from app.mod_passages import Passage
from app.mod_vocab import Entry
from app.utils import check_body

mod_games = Blueprint("games", __name__, url_prefix="/games")

@mod_games.before_request
def before_request():
    parts = request.path.split("/")

    if len(parts) < 3:
        abort(404)
    else:
        game_name = parts[2]

        try:
            g.game = Game[game_name.upper()]
        except:
            abort(404)

@mod_games.route("/<game_name>/play", methods=["GET"])
@login_required
def play_game(game_name, words=None):
    """Retrieves questions to play a game.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return questions for this game
    questions = g.game.question.play_game(words)
    return jsonify(questions)

@mod_games.route("/<game_name>/play/passages/<passage_id>", methods=["GET"])
@login_required
def play_game_for_passage(game_name, passage_id):
    """Plays a game according to the contents of a passage.

    Parameters:
        passage_id: The id of the passage to play this game with.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve the passage with the id passed to us
    passage = Passage.query.filter_by(id=passage_id).first()

    # Return 404 if the passage doesn't exist
    if passage is None:
        return passage_errors.passage_not_found()

    # Load the passage's new words list and use it to return game data
    words = json.loads(passage.new_words)
    return play_game(game_name, words)

@mod_games.route("/<game_name>/finish", methods=["POST"])
@login_required
def finish_game(game_name):
    """Completes a game and stores any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(["correct", "correct_question_ids", "correct_words", "wrong", "wrong_question_ids", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_question_ids = request.json["correct_question_ids"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_question_ids = request.json["wrong_question_ids"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, g.game, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed game result
    game_result = g.game.result(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
    db.session.add(game_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())

@mod_games.route("/<game_name>/questions", methods=["GET"])
@admin_required
def get_questions(game_name):
    """Retrieves all questions for a game.

    Parameters:
        q: The query that should be used for a search.

    Returns:
        JSON data for all the questions.
    """

    questions = []

    if "q" in request.args:
        # Use the query to search for a question if one is included
        query = "%" + request.args.get("q") + "%"

        # Create the filter to use for the search
        filter = g.game.question.id.like(query)
        column_names = g.game.question.__table__.columns.keys()

        for column in column_names:
            filter = filter | getattr(g.game.question, column).like(query)

        # Ensure the correct questions are being returned
        questions = g.game.question.query.filter(filter).all()
    else:
        # Retrieve and return all questions
        questions = g.game.question.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_games.route("/<game_name>/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(game_name, question_id):
    """Retrieves a game's question.

    Returns:
        JSON data of the question.
    """

    question = g.game.question.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_games.route("/<game_name>/questions", methods=["POST"])
@admin_required
def create_question(game_name):
    """Creates a question for a game.

    Body:
        Whatever the necessary parameters are for this game's question.

    Returns:
        JSON data of the new question.
    """

    # Ensure necessary parameters are here
    arguments = inspect.getargspec(g.game.question.__init__).args
    arguments.remove("self")

    if not check_body(arguments):
        return errors.missing_create_question_parameters()

    # Generate data for the question constructor
    data = {key: request.json[key] for key in arguments}

    # Create the question and store it in MySQL
    question = g.game.question(**data)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_games.route("/<game_name>/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(game_name, question_id):
    """Updates attributes for a question.

    Body:
        Whatever the parameters are for this game's question.

    Returns:
        JSON data of the question.
    """

    # Make sure something was passed to us
    if not request.json or len(request.json.keys()) == 0:
        return errors.missing_update_question_parameters()

    # Find the question being updated
    question = g.game.question.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    for key, value in request.json.items():
        question.update(key, value)

    # Save changes in MySQL
    db.session.commit()

    # Return update question JSON data
    return jsonify(question.serialize())
