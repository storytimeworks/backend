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

    # Create array of all stories from JSON data
    stories = Story.query.all()
    stories_data = [story.serialize() for story in stories]

    passages = Passage.query.all()

    # Connect stories with their passages
    for story in stories_data:
        story["passages"] = []

        for passage_id in story["passage_ids"]:
            # Find the passage that matches the next one in the story
            passage = next(x for x in passages if x.id == passage_id)
            passage_data = passage.serialize()

            # Remove actual passage data because the response would be too long
            del passage_data["data"]

            # Add the passage data to this story
            story["passages"].append(passage_data)

    # Update path data with stories array
    path["stories"] = stories_data

    # Return path JSON data
    return jsonify(path)
