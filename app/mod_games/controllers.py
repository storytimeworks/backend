from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import random

from app import db
from app.utils import check_body
import app.mod_games.errors as errors
from app.mod_games.models import Attempt, CopyEditSentence
from app.mod_vocab.models import Entry

mod_games = Blueprint("games", __name__, url_prefix="/games")

@mod_games.route("/flashcard/attempt", methods=["POST"])
@login_required
def log_attempt():
    """Saves a user's answer to a flashcard question.

    Body:
        entry_id: The id of the entry that was shown on the flashcard.
        correct: True if the question was answered correctly.

    Returns:
        JSON data of the question attempt.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["entry_id", "correct"]):
        return errors.missing_attempt_parameters()

    entry_id = request.json["entry_id"]
    correct = request.json["correct"]

    # Create the attempt and store in MySQL
    attempt = Attempt(entry_id, current_user.id, correct)
    db.session.add(attempt)
    db.session.commit()

    # Return JSON data of the attempt
    return jsonify(attempt.serialize())

@mod_games.route("/flashcard/next", methods=["GET"])
@login_required
def get_next_entry():
    """Finds the next flashcard that the current user should see.

    Returns:
        JSON data of the next flashcard.
    """

    # Select a random row from the entries table
    # This is temporary, it will be done with machine learning in the future
    entry = Entry.query.order_by(db.func.rand()).first()
    entry_data = entry.serialize()

    # Figure out if this is the first time the user is seeing this entry
    attempt = Attempt.query.filter_by(entry_id=entry.id, user_id=current_user.id).first()
    entry_data["new"] = attempt is not None

    return jsonify(entry_data)

@mod_games.route("/copy-edit/next", methods=["GET"])
@login_required
def get_next_copy_edit():
    """Finds the next sentence to be shown in the copy edit game.

    Returns:
        JSON data of the next sentence.
    """

    sentence = CopyEditSentence.query.order_by(db.func.rand()).first()

    data = {
        "words": [],
        "explanation": sentence.explanation,
        "correctSentence": sentence.correct_sentence
    }

    for word in sentence.sentence.split("|"):
        datum = {
            "characters": word.replace("c", "")
        }

        if "c" in word:
            datum["correct"] = True

        data["words"].append(datum)

    return jsonify(data)
