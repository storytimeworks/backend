from flask import Blueprint, jsonify, request, session
from flask_login import current_user
import json

from app import db, admin_required
from app.mod_stories import check_body
import app.mod_stories.errors as errors
from app.mod_passages.models import Passage
from app.mod_stories.models import Story

mod_stories = Blueprint("stories", __name__, url_prefix="/stories")

@mod_stories.route("", methods=["GET"])
@admin_required
def get_stories():
    """Retrieves all stories on Storytime.

    Returns:
        JSON data for all of the passages.
    """

    # Retrieve all stories JSON data
    stories = Story.query.all()
    stories_data = [story.serialize() for story in stories]

    # Return JSON data
    return jsonify(stories_data)

@mod_stories.route("/<story_id>", methods=["GET"])
def get_story(story_id):
    """Retrieves a story with the provided story id.

    Args:
        story_id: The id of the story being retrieved.

    Returns:
        The JSON data for this story.
    """

    # Retrieve the story with this id
    story = Story.query.filter_by(id=story_id).first()

    if story:
        # Retrieve all passages associated with this story
        passages = Passage.query.filter(Passage.id.in_(story.passage_ids.split(","))).all()
        story_data = story.serialize()
        story_data["passages"] = passages

        # Return JSON data for this story, with its passages
        return jsonify(story_data)
    else:
        # Return 404 if this story doesn't exist
        return errors.story_not_found()

@mod_stories.route("", methods=["POST"])
@admin_required
def create_story():
    """Creates a story with the provided data.

    Body:
        chinese_name: The chinese name for this story.
        english_name: The english name for this story.
        description: This story's description, in english.

    Returns:
        The JSON data for this story.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["chinese_name", "english_name", "description"]):
        return errors.missing_create_story_parameters()

    chinese_name = request.json["chinese_name"]
    english_name = request.json["english_name"]
    description = request.json["description"]

    # Create the story and add it to MySQL
    story = Story(chinese_name, english_name, description)
    db.session.add(story)
    db.session.commit()

    # Return the story JSON data
    return get_story(story.id)

@mod_stories.route("/<story_id>", methods=["PUT"])
@admin_required
def update_stories(story_id):
    """Updates the specified story. Right now, only one property can be updated
    at a time.

    Args:
        story_id: The id of the story being updated.

    Body:
        chinese_name: The chinese name of this passage.
        english_name: The english name of this passage.
        description: A description of the story, in english.
        passage_ids: A comma-separated list of the ids of the passages in the story.

    Returns:
        The new story JSON data.
    """

    key = None
    value = None

    # Try to get the key and value being updated for this entry
    if request.json and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_story_parameters()

    # Find the story being updated
    story = Story.query.filter_by(id=story_id).first()

    # Return 404 if the story doesn't exist
    if not story:
        return errors.story_not_found()

    # Update the story accordingly, depending on the key and value
    if key == "chinese_name":
        story.chinese_name = value
    elif key == "english_name":
        story.english_name = value
    elif key == "description":
        story.description = value
    elif key == "passage_ids":
        story.passage_ids = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated story JSON data
    return get_story(story_id)
