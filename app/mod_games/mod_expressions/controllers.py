from flask import Blueprint, jsonify, request

from app import db, admin_required
from app.mod_games.mod_expressions import check_body
import app.mod_games.mod_expressions.errors as errors
from app.mod_games.mod_expressions.models import ExpressionsQuestion

mod_expressions_game = Blueprint("expressions_game", __name__, url_prefix="/games/expressions")

@mod_expressions_game.route("", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all expressions game questions.

    Parameters:
        q: The query that should be used for the search.

    Returns:
        JSON data for all the questions.
    """

    questions = []

    if "q" in request.args:
        # Use the query to search for a question if one is included
        query = "%" + request.args.get("q") + "%"

        # Ensure the correct questions are being returned
        questions = ExpressionsQuestion.query.filter(
            ExpressionsQuestion.prompt.like(query) |
            ExpressionsQuestion.correct_choice.like(query) |
            ExpressionsQuestion.choice_2.like(query) |
            ExpressionsQuestion.choice_3.like(query) |
            ExpressionsQuestion.choice_4.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = ExpressionsQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_expressions_game.route("/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a question with a specific id.

    Arguments:
        question_id: The id of this question.

    Returns:
        JSON data for this question.
    """

    question = ExpressionsQuestion.query.filter_by(id=question_id).first()

    if not question:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_expressions_game.route("", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for the expressions game.

    Body:
        prompt: The prompt for this question.
        correct_choice: The correct answer to this question.
        choice_2: The first wrong answer to this question.
        choice_3: The second wrong answer to this question.
        choice_4: The third wrong answer to this question.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompt", "correct_choice", "choice_2", "choice_3", "choice_4"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"]
    correct_choice = request.json["correct_choice"]
    choice_2 = request.json["choice_2"]
    choice_3 = request.json["choice_3"]
    choice_4 = request.json["choice_4"]

    # Create the question and store in MySQL
    question = ExpressionsQuestion(prompt, correct_choice, choice_2, choice_3, choice_4)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_expressions_game.route("/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a question for the expressions game. Currently only one key can
    be updated at a time.

    Body:
        prompt: The prompt for this question.
        correct_choice: The correct answer to this question.
        choice_2: The first wrong answer to this question.
        choice_3: The second wrong answer to this question.
        choice_4: The third wrong answer to this question.

    Returns:
        JSON data of the question.
    """

    key = None
    value = None

    # Try to get the key and value being updated for this question
    if request.json and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_question_parameters()

    # Find the question being updated
    question = ExpressionsQuestion.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if not question:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "prompt":
        question.prompt = value
    elif key == "correct_choice":
        question.correct_choice = value
    elif key == "choice_2":
        question.choice_2 = value
    elif key == "choice_3":
        question.choice_3 = value
    elif key == "choice_4":
        question.choice_4 = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated question JSON data
    return jsonify(question.serialize())
