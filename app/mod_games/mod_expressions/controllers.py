from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db, admin_required
import app.mod_games.mod_expressions.errors as errors
from app.mod_games.mod_expressions.models import ExpressionsQuestion
from app.utils import check_body

mod_expressions_game = Blueprint("expressions_game", __name__, url_prefix="/games/expressions")

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
