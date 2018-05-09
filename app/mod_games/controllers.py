from flask import Blueprint, jsonify, request
from flask_login import current_user
import random

from app import db
from app.mod_games import check_body
import app.mod_games.errors as errors
from app.mod_games.models import Attempt

mod_games = Blueprint("games", __name__, url_prefix="/games")

@mod_games.route("/flashcard/attempt", methods=["POST"])
def log_attempt():
    if not check_body(request, ["entry_id", "correct"]):
        return errors.missing_attempt_parameters()

    entry_id = request.json["entry_id"]
    correct = request.json["correct"]

    if not current_user.is_active:
        return errors.not_authenticated()

    attempt = Attempt(entry_id, current_user.id, correct)
    db.session.add(attempt)
    db.session.commit()

    return jsonify(attempt.serialize())
