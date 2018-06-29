from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required
import jieba, json, numpy as np
from pypinyin import pinyin

from app import db, admin_required
import app.mod_passages.errors as errors
from app.mod_passages.models import Passage, ChineseNameCharacter
from app.mod_path.models import PathAction
from app.mod_stories.models import Story
from app.mod_users.models import User
from app.utils import check_body

mod_passages = Blueprint("passages", __name__, url_prefix="/passages")

@mod_passages.route("", methods=["GET"])
@admin_required
def get_passages():
    """Retrieves all passages on Storytime.

    Returns:
        JSON data for all of the passages.
    """

    # Return all passages JSON data
    passages = Passage.query.all()
    passages_data = [passage.serialize() for passage in passages]
    return jsonify(passages_data)

def passage_status_for_user(passage_id, user_id):
    # Create array of all stories from JSON data
    stories = Story.query.order_by(Story.position.asc()).all()
    stories_data = [story.serialize() for story in stories]

    # Create array of completed passage ids
    path_actions = PathAction.query.filter_by(user_id=user_id).all()
    completed_passage_ids = [action.passage_id for action in path_actions]

    # Loop through the passages in order
    for story in stories_data:
        for story_passage_id in story["passage_ids"]:
            # Check if this passage has been completed
            if story_passage_id in completed_passage_ids:
                if story_passage_id == passage_id:
                    # Return complete if this is the passage we're looking for
                    return "complete"
                else:
                    # Otherwise, keep going through the passages, in order
                    continue
            else:
                # We get here the first time we find a passage that hasn't been
                # completed, so if it's the passage we're looking for, this is
                # the user's next passage. Otherwise, we haven't found the
                # passage yet, so it is locked.
                if story_passage_id == passage_id:
                    return "next"
                else:
                    return "locked"

@mod_passages.route("/<passage_id>", methods=["GET"])
@login_required
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
        passage_data = passage.serialize()

        # If someone is logged in, check what their status is for this passage
        if current_user.is_admin:
            passage_data["status"] = "completed"
        else:
            passage_data["status"] = passage_status_for_user(int(passage_id), current_user.id)

            # If the user hasn't reached this passage yet, return 403
            if passage_data["status"] == "locked":
                return errors.passage_not_reached()

        # Extract the words in each text component and add to JSON response
        for idx, component in enumerate(passage_data["data"]["components"]):
            if component["type"] == "text":
                # Separate Chinese sentences into separate words
                word_generator = jieba.cut(component["text"], cut_all=False)
                words = [{"chinese": word, "punctuation": False} for word in word_generator]

                # Add pinyin to the word objects
                pinyin_words = [pinyin(word["chinese"]) for word in words]
                flattened_pinyin_words = [[j for i in words for j in i] for words in pinyin_words]
                joined_pinyin_words = [" ".join(words) for words in flattened_pinyin_words]

                # True if the next word in the loop needs to be capitalized
                capitalize_next_word = True

                for i, _ in enumerate(words):
                    word = joined_pinyin_words[i]

                    if capitalize_next_word:
                        # Capitalize this word, don't capitalize the next one
                        word = word.capitalize()
                        capitalize_next_word = False

                    # Replace Chinese punctutation with regular punctuation
                    if word == "。":
                        capitalize_next_word = True
                        word = "."
                        words[i]["punctuation"] = True
                    elif word == "，":
                        word = ","
                        words[i]["punctuation"] = True
                    elif word == "！":
                        capitalize_next_word = True
                        word = "!"
                        words[i]["punctuation"] = True
                    elif word == "？":
                        capitalize_next_word = True
                        word = "?"
                        words[i]["punctuation"] = True

                    words[i]["pinyin"] = word

                # Add the words to the passage data
                passage_data["data"]["components"][idx]["words"] = words

        return jsonify(passage_data)
    else:
        # Return 404 if this passage doesn't exist
        return errors.passage_not_found()

@mod_passages.route("", methods=["POST"])
@admin_required
def create_passage():
    """Creates a passage with the provided data.

    Body:
        name: The name of this passage.
        description: This passage's description, in english.
        story_id: The id of the story that this passage corresponds to.

    Returns:
        The JSON data for the new passage.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["name", "description", "story_id"]):
        return errors.missing_create_passage_parameters()

    name = request.json["name"]
    description = request.json["description"]
    story_id = request.json["story_id"]

    # Create the passage and add it to MySQL
    passage = Passage(name, description, story_id)
    db.session.add(passage)

    # Update the story to add this passage id
    story = Story.query.filter_by(id=story_id).first()
    passage_ids = json.loads(story.passage_ids)
    passage_ids.append(passage.id)
    story.passage_ids = json.dumps(passage_ids)
    db.session.commit()

    # Return the passage JSON data
    return get_passage(passage.id)

def update_word_lists():
    """Updates the list of new words for all passages, in order of appearance.
    """

    # Retrieve all stories first in order to order the passages correctly
    stories = Story.query.order_by(Story.position.asc()).all()
    passage_ids = []

    # Create a correctly ordered list of passage ids
    for story in stories:
        story_passage_ids = json.loads(story.passage_ids)
        passage_ids.extend(story_passage_ids)

    # Get all of the passages by the ids that are in the list
    passages = Passage.query.filter(Passage.id.in_(passage_ids)).all()

    # Sort the retrieved passages according to the order of passage_ids, since
    # the database query doesn't preserve ordering
    sorted_passages = sorted(passages, key=lambda x: passage_ids.index(x.id))

    # Keep track of all words in all passages
    words = []

    for passage in passages:
        # Get the components of each passage
        components = json.loads(passage.data)["components"]
        passage_words = []

        # Use jieba to find the words in each text component
        for component in components:
            if component["type"] == "text":
                passage_words.extend([word for word in jieba.cut(component["text"], cut_all=False)])

        # Use numpy to figure out which words have appeared for the first time
        new_words = np.setdiff1d(passage_words, words).tolist()

        # Remove punctuation from new words list
        punctuation_words = ["。", "，", "！", "？"]
        new_words = [word for word in new_words if word not in punctuation_words]

        passage.new_words = json.dumps(new_words)

        # Add the new words to the general words array
        words.extend(new_words)

    # Save all changes in MySQL
    db.session.commit()

@mod_passages.route("/<passage_id>", methods=["PUT"])
@admin_required
def update_passage(passage_id):
    """Updates the specified passage. Right now, only one property can be
    updated at a time.

    Args:
        passage_id: The id of the passage being updated.

    Body:
        name: The name of this passage.
        description: A description of the passage, in english.
        data: The passage's components' data.
        notes: The passage's grammar notes.

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

    # Find the passage being updated
    passage = Passage.query.filter_by(id=passage_id).first()

    # Return 404 if the passage doesn't exist
    if not passage:
        return errors.passage_not_found()

    # Update the passage accordingly, depending on the key and value
    if key == "name":
        passage.name = value
    elif key == "description":
        passage.description = value
    elif key == "data":
        passage.data = json.dumps(value)

        # Update all word lists to reflect any edits made
        update_word_lists()
    elif key == "notes":
        passage.notes = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated passage JSON data
    return get_passage(passage_id)

@mod_passages.route("/<passage_id>/finish", methods=["PATCH"])
@login_required
def finish_passage(passage_id):
    """Marks a passage as complete for the authenticated user.

    Args:
        passage_id: The id of the passage being completed.

    Returns:
        204 no content.
    """

    action = PathAction(passage_id, current_user.id)
    db.session.add(action)
    db.session.commit()

    return ("", 204)

@mod_passages.route("/name", methods=["GET"])
def generate_chinese_name():
    # 0 = intelligence, 1 = grace/elegance, 2 = strength/power, 3 = fortune, 4 = beauty/appearance
    attribute = int(request.args.get("attribute"))
    gender = int(request.args.get("gender"))

    surname = ChineseNameCharacter.query.filter_by(position=0).order_by(db.func.rand()).first()
    given_name_p1 = ChineseNameCharacter.query.filter_by(position=1, attribute=attribute).filter((ChineseNameCharacter.gender == gender) | (ChineseNameCharacter.gender.is_(None))).order_by(db.func.rand()).first()
    given_name_p2 = ChineseNameCharacter.query.filter_by(position=2).filter((ChineseNameCharacter.gender == gender) | (ChineseNameCharacter.gender.is_(None))).order_by(db.func.rand()).first()

    data = [
        {
            "character": surname.name_character,
            "pinyin": pinyin(surname.name_character)[0][0]
        },
        {
            "character": given_name_p1.name_character,
            "meaning": given_name_p1.meaning,
            "pinyin": pinyin(given_name_p1.name_character)[0][0]
        },
        {
            "character": given_name_p2.name_character,
            "meaning": given_name_p2.meaning,
            "pinyin": pinyin(given_name_p2.name_character)[0][0]
        }
    ]

    return jsonify(data)
