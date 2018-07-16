from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import json
from pypinyin import pinyin

from app import admin_required, db
from app.mod_games.models import GameResult
import app.mod_games.mod_compound.errors as errors
from app.mod_games.mod_compound.models import CompoundQuestion, CompoundResult
from app.mod_mastery import update_masteries
from app.utils import check_body

mod_compound_game = Blueprint("compound_game", __name__, url_prefix="/games/compound")

@mod_compound_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 10 questions in order to play Compound.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return Compound questions for this user
    questions = CompoundQuestion.play_game()
    return jsonify(questions)

@mod_compound_game.route("/finish", methods=["POST"])
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
    result = GameResult(current_user.id, 3, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Compound game result
    compound_result = CompoundResult(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
    db.session.add(compound_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())

@mod_compound_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all Compound questions.

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
        questions = CompoundQuestion.query.filter(
            CompoundQuestion.prompt.like(query) |
            CompoundQuestion.choices.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = CompoundQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_compound_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a Compound question.

    Returns:
        JSON data of the question.
    """

    question = CompoundQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_compound_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for Compound.

    Body:
        choices: The array of choices that users can pick from.
        prompt: The english prompt for this question.

    Returns:
        JSON data of this question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompt", "choices"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"]
    choices = request.json["choices"]

    # Create the question and store it in MySQL
    question = CompoundQuestion(prompt, choices)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_compound_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a Compound question. Currently only one key can be updated at a
    time.

    Body:
        choices: The array of choices that users can pick from.
        prompt: The english prompt for this question.

    Returns:
        JSON data of this question.
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
    question = CompoundQuestion.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "choices":
        print(request.json)
        question.choices = json.dumps(value)

        # Also update pinyin_choices when choices are being updated
        pinyin_choices = value

        for idx, choice in enumerate(pinyin_choices):
            for jdx, option in enumerate(choice):
                pinyin_choices[idx][jdx] = pinyin(option)[0][0]

        question.pinyin_choices = json.dumps(pinyin_choices)
    elif key == "prompt":
        question.prompt = value

    # Save changes in MySQL
    db.session.commit()

    # Return update question JSON data
    return jsonify(question.serialize())
