from flask import Blueprint, jsonify, request
from flask_login import current_user
import random

from app import db
from app.mod_games import check_body
import app.mod_games.errors as errors
from app.mod_games.models import Attempt
from app.mod_vocab.models import Entry

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

@mod_games.route("/flashcard/next", methods=["GET"])
def get_next_entry():
    if not current_user.is_active:
        return errors.not_authenticated()

    entry_id = random.randint(1, 240)
    entry = Entry.query.filter_by(id=entry_id).first()
    entry_data = entry.serialize()

    attempt = Attempt.query.filter_by(entry_id=entry_id, user_id=current_user.id).first()

    if not attempt:
        entry_data["new"] = True
    else:
        entry_data["new"] = False

    return jsonify(entry_data)
