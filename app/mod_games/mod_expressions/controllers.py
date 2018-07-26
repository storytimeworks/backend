from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db, admin_required
import app.mod_games.mod_expressions.errors as errors
from app.mod_games.mod_expressions.models import ExpressionsQuestion
from app.utils import check_body

mod_expressions_game = Blueprint("expressions_game", __name__, url_prefix="/games/expressions")

@mod_expressions_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 30 questions in order to play a game.

    Returns:
        JSON data for all of the questions.
    """

    # Get questions that don't have other questions that come before it
    questions = ExpressionsQuestion.query \
        .filter(ExpressionsQuestion.preceded_by == None) \
        .order_by(db.func.rand()).limit(30).all()

    # Loop through all of the questions
    for idx in range(len(questions)):
        while questions[idx].followed_by != None:
            # Add questions that follow the questions that were retrieved
            question = ExpressionsQuestion.query.filter_by(id=questions[idx].followed_by).first()
            questions.insert(idx + 1, question)
            idx += 1

    # Return JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_expressions_game.route("/questions", methods=["GET"])
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
            ExpressionsQuestion.choice_1.like(query) |
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

@mod_expressions_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a question with a specific id.

    Arguments:
        question_id: The id of this question.

    Returns:
        JSON data for this question.
    """

    question = ExpressionsQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_expressions_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for the expressions game.

    Body:
        prompt: The prompt for this question.
        choice_1: The first choice to answer this question.
        choice_2: The second choice to answer this question.
        choice_3: The third choice to answer this question.
        choice_4: The fourth choice to answer this question.
        choice_1_correct: True if the first choice is correct.
        choice_2_correct: True if the second choice is correct.
        choice_3_correct: True if the third choice is correct.
        choice_4_correct: True if the fourth choice is correct.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompt", "choice_1", "choice_2", "choice_3", "choice_4", "choice_1_correct", "choice_2_correct", "choice_3_correct", "choice_4_correct"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"].strip()
    choice_1 = request.json["choice_1"].strip()
    choice_2 = request.json["choice_2"].strip()
    choice_3 = request.json["choice_3"].strip()
    choice_4 = request.json["choice_4"].strip()
    choice_1_correct = request.json["choice_1_correct"]
    choice_2_correct = request.json["choice_2_correct"]
    choice_3_correct = request.json["choice_3_correct"]
    choice_4_correct = request.json["choice_4_correct"]

    # Create the question and store in MySQL
    question = ExpressionsQuestion(prompt, choice_1, choice_2, choice_3, choice_4, choice_1_correct, choice_2_correct, choice_3_correct, choice_4_correct)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_expressions_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a question for the expressions game. Currently only one key can
    be updated at a time.

    Body:
        prompt: The prompt for this question.
        choice_1: The first choice to answer this question.
        choice_2: The second choice to answer this question.
        choice_3: The third choice to answer this question.
        choice_4: The fourth choice to answer this question.
        choice_1_correct: True if the first choice is correct.
        choice_2_correct: True if the second choice is correct.
        choice_3_correct: True if the third choice is correct.
        choice_4_correct: True if the fourth choice is correct.
        followed_by: The id of the question that follows this one, if any.
        preceded_by: The id of the question that comes before this one, if any.

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
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "prompt":
        question.prompt = value.strip()
    elif key == "choice_1":
        question.choice_1 = value.strip()
    elif key == "choice_2":
        question.choice_2 = value.strip()
    elif key == "choice_3":
        question.choice_3 = value.strip()
    elif key == "choice_4":
        question.choice_4 = value.strip()
    elif key == "choice_1_correct":
        question.choice_1_correct = value
    elif key == "choice_2_correct":
        question.choice_2_correct = value
    elif key == "choice_3_correct":
        question.choice_3_correct = value
    elif key == "choice_4_correct":
        question.choice_4_correct = value
    elif key == "followed_by":
        question.followed_by = value
    elif key == "preceded_by":
        question.preceded_by = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated question JSON data
    return jsonify(question.serialize())

@mod_expressions_game.route("/choices", methods=["GET"])
@admin_required
def get_all_choices():
    """Retrieves all choices present in the expressions game.

    Returns:
        All choices, as a JSON string array.
    """

    # Retrieve all questions to get choices from
    questions = ExpressionsQuestion.query.all()

    # Create empty choices array
    choices = []

    # Add all possible choices to the array
    for question in questions:
        choices.append(question.choice_1)
        choices.append(question.choice_2)
        choices.append(question.choice_3)
        choices.append(question.choice_4)

    # Make sure only one of each choice is here
    choices = list(set(choices))

    # Return data as JSON
    return jsonify(choices)
