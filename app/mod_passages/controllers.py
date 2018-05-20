from flask import Blueprint, jsonify, request, session
from flask_login import current_user
import json

from app import db
from app.mod_passages import check_body
import app.mod_passages.errors as errors
from app.mod_passages.models import Passage
from app.mod_users.models import User

mod_passages = Blueprint("passages", __name__, url_prefix="/passages")

@mod_passages.route("", methods=["GET"])
def get_passages():
    """Retrieves all passages on Storytime.

    Returns:
        JSON data for all of the passages.
    """

    # Ensure that the person making this request is authenticated and an admin
    if not current_user.is_active:
        return errors.missing_authentication()
    elif not current_user.is_admin:
        return errors.unauthorized()

    # Return all passages JSON data
    passages = Passage.query.all()
    passages_data = [passage.serialize() for passage in passages]
    return jsonify(passages_data)

@mod_passages.route("/<passage_id>", methods=["GET"])
def get_passage(passage_id):
    """Retrieves a passage with the provided passage id.

    Args:
        passage_id: The id of the passage being retrieved.

    Returns:
        The JSON data for this passage.
    """

    # Retrieve the passage with this id
    passage = Passage.query.filter_by(id=passage_id).first()

    if passage:
        # Return JSON data if the passage could be found
        return jsonify(passage.serialize())
    else:
        # Return 404 if this passage doesn't exist
        return errors.passage_not_found()

@mod_passages.route("", methods=["POST"])
def create_passage():
    """Creates a passage with the provided data.

    Body:
        chinese_name: The chinese name for this passage.
        english_name: The english name for this passage.
        description: This passage's description, in english.
        story_id: The id of the story that this passage corresponds to.

    Returns:
        The JSON data for the new passage.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["chinese_name", "english_name", "description", "story_id"]):
        return errors.missing_create_passage_parameters()

    chinese_name = request.json["chinese_name"]
    english_name = request.json["english_name"]
    description = request.json["description"]
    story_id = request.json["story_id"]

    # Ensure the person making this request is authenticated and an admin
    if not current_user.is_active:
        return errors.missing_authentication()
    elif not current_user.is_admin:
        return errors.unauthorized()

    # Add one component to the passage by default
    default_data = {
        "components": [{
            "text": "你好",
            "type": "text"
        }]
    }

    data = json.dumps(default_data)

    # Create the passage and add it to MySQL
    passage = Passage(chinese_name, english_name, description, story_id, data)
    db.session.add(passage)
    db.session.commit()

    # Return the passage JSON data
    return get_passage(passage.id)

@mod_passages.route("/<passage_id>", methods=["PUT"])
def update_passage(passage_id):
    """Updates the specified passage. Right now, only one property can be
    updated at a time.

    Args:
        passage_id: The id of the passage being updated.

    Body:
        chinese_name: The chinese name of this passage.
        english_name: The english name of this passage.
        description: A description of the passage, in english.
        data: The passage's components' data.

    Returns:
        The new passage JSON data.
    """

    key = None
    value = None

    # Try to get the key and value being updated for this entry
    if request.json and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_passage_parameters()

    # Ensure that the person making this request is authenticated and is an admin
    if not current_user.is_active:
        return errors.missing_authentication()
    elif not current_user.is_admin:
        return errors.unauthorized()

    # Find the passage being updated
    passage = Passage.query.filter_by(id=passage_id).first()

    # Return 404 if the passage doesn't exist
    if not passage:
        return errors.passage_not_found()

    # Update the passage accordingly, depending on the key and value
    if key == "chinese_name":
        passage.chinese_name = value
    elif key == "english_name":
        passage.english_name = value
    elif key == "description":
        passage.description = value
    elif key == "data":
        passage.data = json.dumps(value)

    # Save changes in MySQL
    db.session.commit()

    # Return updated passage JSON data
    return get_passage(passage_id)
