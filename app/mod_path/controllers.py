from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required

from app.mod_passages.models import Passage
from app.mod_stories.models import Story

mod_path = Blueprint("path", __name__, url_prefix="/path")

@mod_path.route("", methods=["GET"])
@login_required
def get_path():
    """Retrieves the current user's path on Storytime.

    Returns:
        JSON data of the user's path.
    """

    path = {
        "stories": []
    }

    stories = Story.query.all()
    stories_data = [story.serialize() for story in stories]

    passages = Passage.query.all()

    for story in stories_data:
        story["passages"] = []

        for passage_id in story["passage_ids"]:
            passage = next(x for x in passages if x.id == passage_id)
            passage_data = passage.serialize()
            del passage_data["data"]

            story["passages"].append(passage_data)

    path["stories"] = stories_data
    return jsonify(path)
