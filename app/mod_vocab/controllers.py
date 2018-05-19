from flask import Blueprint, jsonify, request, session
from flask_login import current_user

import json

from app import db
from app.mod_vocab import check_body
import app.mod_vocab.errors as errors
from app.mod_vocab.models import Entry, Sentence
from app.mod_users.models import User

mod_vocab = Blueprint("vocab", __name__, url_prefix="/vocabulary")

@mod_vocab.route("/entries", methods=["GET"])
def get_entries():
    """Searches for entries matching a query. If no query is included, the first
    entries we can find are the ones that are returned.

    Parameters:
        q: The query that should be used for the search.

    Returns:
        The data for all entries that match the query.
    """

    entries = []

    if "q" in request.args:
        # Use the query to search for an entry if one is included
        query = "%" + request.args.get("q") + "%"

        # Ensure the correct entries are being returned
        entries = Entry.query.filter( \
            ((Entry.chinese.like(query) | Entry.pinyin.like(query)) & (Entry.source_is_chinese == True) | \
            (Entry.english.like(query) & (Entry.source_is_chinese == False))) \
        ).all()
    else:
        # Retrieve all entries if no query is provided
        entries = Entry.query.all()

    # Return entries JSON data
    entries_data = [entry.serialize() for entry in entries]
    return jsonify(entries_data)

@mod_vocab.route("/entries/<entry_id>", methods=["GET"])
def get_entry(entry_id):
    """Retrieves data for an entry.

    Args:
        entry_id: The id of the entry that is being requested.

    Returns:
        The JSON data for this entry.
    """

    # Find entry in the SQL database
    entry = Entry.query.filter_by(id=entry_id).first()

    if entry:
        # Return the entry's JSON data
        return jsonify(entry.serialize())
    else:
        # Return 404 if there is no entry with this id
        return errors.entry_not_found()

@mod_vocab.route("/entries", methods=["POST"])
def create_entry():
    """Creates a new vocabulary entry.

    Body:
        chinese: The chinese characters for this entry.
        english: The english translation of this entry.
        pinyin: The pinyin representation of the chinese characters.
        source_is_chinese: Not used for now, should be set to True.

    Returns:
        The JSON data for the new entry.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["chinese", "english", "pinyin", "source_is_chinese"]):
        return errors.missing_create_entry_parameters()

    chinese = request.json["chinese"]
    english = request.json["english"]
    pinyin = request.json["pinyin"]
    source_is_chinese = request.json["source_is_chinese"]

    # Ensure that the person making this request is authenticated and is an admin
    if not current_user.is_active or not current_user.is_admin:
        return errors.missing_authentication()

    # Add the new entry to the database
    entry = Entry(chinese, english, pinyin, source_is_chinese)
    db.session.add(entry)
    db.session.commit()

    # Return JSON data for the new entry
    return get_entry(entry.id)

@mod_vocab.route("/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    """Updates an existing vocabulary entry. Currently only one key can be
    updated at a time.

    Body:
        chinese: The chinese characters for this entry.
        english: The english translation of this entry.
        pinyin: The pinyin representation of the chinese characters.
        source_is_chinese: Not used for now, should be set to True.
        translations: JSON string representing the translations of this entry.
        categories: JSON string representing the categories this entry falls under.

    Returns:
        The JSON data for the updated entry.
    """

    key = None
    value = None

    # Try to get the key and value being updated for this entry
    if request.json:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_entry_parameters()

    # Ensure that the person making this request is authenticated and is an admin
    if not current_user.is_active or not current_user.is_admin:
        return errors.missing_authentication()

    # Find the entry being updated
    entry = Entry.query.filter_by(id=entry_id).first()

    # Return 404 if the entry doesn't exist
    if not entry:
        return errors.entry_not_found()

    # Update the entry accordingly, depending on the key and value
    if key == "chinese":
        entry.chinese = value
    elif key == "english":
        entry.english = value
    elif key == "pinyin":
        entry.pinyin = value
    elif key == "source_is_chinese":
        entry.source_is_chinese = value
    elif key == "translations":
        entry.translations = json.dumps(value)
    elif key == "categories":
        entry.categories = json.dumps(value)

    # Save changes in MySQL
    db.session.commit()

    # Return updated entry JSON data
    return get_entry(entry_id)

@mod_vocab.route("/health", methods=["GET"])
def get_entries_health():
    """Returns health data about vocabulary entries.

    Returns:
        JSON data with vocabulary health data.
    """

    # Ensure the current user is logged in and an admin
    if not current_user.is_active or not current_user.is_admin:
        return errors.missing_authentication()

    # Retrieve all vocabulary entries that need translations
    entries = Entry.query.filter_by(source_is_chinese=True, translations="[]").all()
    entries_data = [entry.serialize() for entry in entries]

    # Find how many entries are in the database (to calculate percentages)
    entries_num = Entry.query.count()

    # Return JSON health data
    return jsonify(
        no_translations=entries_data,
        data={
            "total": entries_num
        }
    )

@mod_vocab.route("/sentences", methods=["GET"])
def get_sentences():
    """Retrieves Chinese and English sentences that match a given query.

    Parameters:
        q: The query to search for sentences with.

    Returns:
        The first 10 sentences that can be found that match this query.
    """

    # Get the query parameter if there is one
    q = request.args.get("q")
    sentences = None

    if q:
        # Retrieve 10 sentences with a query
        query = "%" + request.args.get("q") + "%"
        sentences = Sentence.query.filter(Sentence.chinese.like(query)).limit(10).all()
    else:
        # Retrieve the first 10 sentences we can find
        sentences = Sentence.query.limit(10).all()

    # Return JSON sentences data
    sentences_data = [sentence.serialize() for sentence in sentences]
    return jsonify(sentences_data)
