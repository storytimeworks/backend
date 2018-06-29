from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required

from app.mod_passages.models import Passage
from app.mod_path.models import PathAction
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
    stories = Story.query.order_by(Story.position.asc()).all()
    stories_data = [story.serialize() for story in stories]

    passages = Passage.query.all()

    # Figure out which passages have been completed
    path_actions = PathAction.query.filter_by(user_id=current_user.id).all()
    completed_passage_ids = []

    # Create a dictionary that maps passage ids to their actions
    path_actions_by_passage = {}

    for action in path_actions:
        # Add this part to the passage's actions list
        if action.passage_id in path_actions_by_passage:
            path_actions_by_passage[action.passage_id].append(action.part)
        else:
            path_actions_by_passage[action.passage_id] = [action.part]

        # Create array for convenience
        actions = path_actions_by_passage[action.passage_id]

        # Check if all parts of this passage have been completed
        if 0 in actions and 1 in actions and 2 in actions and 3 in actions and action.passage_id not in completed_passage_ids:
            completed_passage_ids.append(action.passage_id)

    # True if we've reached the user's furthest passage in the following loop
    reached_furthest_passage = False

    # Connect stories with their passages
    for story in stories_data:
        story["passages"] = []

        for passage_id in story["passage_ids"]:
            # Find the passage that matches the next one in the story
            passage = next(x for x in passages if x.id == passage_id)
            passage_data = passage.serialize()

            # Remove actual passage data because the response would be too long
            del passage_data["data"]

            if reached_furthest_passage:
                # If we've already reached the furthest passage, this one should
                # be locked
                passage_data["status"] = "locked"
            else:
                # If we haven't reached the furthest passage yet, determine if
                # the user has completed this one
                if passage_id in completed_passage_ids:
                    passage_data["status"] = "complete"
                else:
                    # If not, this is the user's current passage and we've
                    # reached their furthest passage
                    if passage_id in path_actions_by_passage:
                        # If this passage has any actions, it is in progress
                        passage_data["status"] = "in_progress"
                    else:
                        # Otherwise, it is the user's next passage
                        passage_data["status"] = "next"

                    reached_furthest_passage = True

            # Admins have every passage unlocked
            if current_user.is_admin:
                passage_data["status"] = "complete"

            # Add the passage data to this story
            story["passages"].append(passage_data)

        # Get all of the different passage statuses in this story
        passage_statuses = list(set([passage["status"] for passage in story["passages"]]))

        if len(passage_statuses) == 1:
            # If all of the statuses are the same, this should be the status for
            # the story as well
            story["status"] = passage_statuses[0]
        else:
            # Otherwise, it must contain a passage with the status of "next"
            story["status"] = "next"

    # Update path data with stories array
    path["stories"] = stories_data

    # Return path JSON data
    return jsonify(path)
