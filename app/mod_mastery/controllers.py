from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.mod_mastery.models import Mastery

mod_mastery = Blueprint("mastery", __name__, url_prefix="/mastery")

@mod_mastery.route("", methods=["GET"])
@login_required
def get_user_masteries():
    """Retrieves all of a user's mastery data.

    Returns:
        JSON data about the user's mastery with every word.
    """

    masteries = Mastery.query.all()
    return jsonify([mastery.serialize() for mastery in masteries])
