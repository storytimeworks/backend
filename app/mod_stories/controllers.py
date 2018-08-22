from flask import Blueprint, jsonify, request, session
from flask_login import current_user
import json

from app import db, admin_required
import app.mod_stories.errors as errors
from app.mod_passages import Passage
from app.mod_stories import Story
from app.utils import check_body

mod_stories = Blueprint("stories", __name__, url_prefix="/stories")

@mod_stories.route("", methods=["GET"])
@admin_required
def get_stories():
    """Retrieves all stories on Storytime.

    Returns:
        JSON data for all of the stories.
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
        passages = Passage.query.filter(Passage.id.in_(json.loads(story.passage_ids))).all()
        passages_data = [passage.serialize() for passage in passages]

        story_data = story.serialize()
        story_data["passages"] = passages_data

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
        name: The name of this story.
        description: This story's description, in english.
        position: The position that this story is in, relative to other stories.

    Returns:
        The JSON data for this story.
    """

    # Check that all necessary data is in the request body
    if not check_body(["name", "description", "position"]):
        return errors.missing_create_story_parameters()

    name = request.json["name"]
    description = request.json["description"]
    position = request.json["position"]

    # Create the story and add it to MySQL
    story = Story(name, description, position)
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
        name: The name of this story.
        description: A description of the story, in english.
        passage_ids: A comma-separated list of the ids of the passages in the story.
        position: The position that this story is in, relative to other stories.

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
    if key == "name":
        story.name = value
    elif key == "description":
        story.description = value
    elif key == "passage_ids":
        story.passage_ids = json.dumps(value)
    elif key == "position":
        story.position = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated story JSON data
    return get_story(story_id)
