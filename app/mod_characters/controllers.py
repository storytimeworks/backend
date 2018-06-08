from flask import Blueprint, jsonify
from app.mod_characters.models import Character

mod_characters = Blueprint("characters", __name__, url_prefix="/characters")

@mod_characters.route("", methods=["GET"])
def get_characters():
    """Retrieves all characters on Storytime.

    Returns:
        JSON data for all of the characters.
    """

    # Retrieve all characters JSON data
    characters = Character.query.all()
    characters_data = [character.serialize() for character in characters]

    # Return JSON data
    return jsonify(characters_data)
