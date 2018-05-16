from flask import Blueprint, jsonify, request, session

import json

from app import db
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
    if "user_id" not in session:
        return errors.missing_authentication()
    else:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()

        if user:
            if 1 not in json.loads(user.groups):
                return errors.not_authorized()
            else:
                # User is authenticated and authorized to do this
                pass
        else:
            return errors.invalid_session()

    chinese = request.json["chinese"]
    english = request.json["english"]
    pinyin = request.json["pinyin"]
    source_is_chinese = request.json["source_is_chinese"]

    entry = Entry(chinese, english, pinyin, source_is_chinese)
    db.session.add(entry)
    db.session.commit()

    return get_entry(entry.id)

@mod_vocab.route("/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    if "user_id" not in session:
        return errors.missing_authentication()
    else:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()

        if user:
            if 1 not in json.loads(user.groups):
                return errors.not_authorized()
            else:
                # User is authenticated and authorized to do this
                pass
        else:
            return errors.invalid_session()

    key = list(request.json.keys())[0]
    value = request.json[key]

    entry = Entry.query.filter_by(id=entry_id).first()

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

    db.session.commit()

    return get_entry(entry_id)

@mod_vocab.route("/health", methods=["GET"])
def get_entries_info():
    if "user_id" not in session:
        return errors.missing_authentication()
    else:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()

        if user:
            if 1 not in json.loads(user.groups):
                return errors.not_authorized()
            else:
                # User is authenticated and authorized to do this
                pass
        else:
            return errors.invalid_session()

    entries = Entry.query.filter_by(source_is_chinese=True, translations="[]").all()
    entries_data = [entry.serialize() for entry in entries]

    entries_num = Entry.query.count()
    return jsonify(no_translations=entries_data, data={"total": entries_num})

@mod_vocab.route("/sentences", methods=["GET"])
def get_sentences():
    query = "%" + request.args.get("q") + "%"
    sentences = Sentence.query.filter(Sentence.chinese.like(query)).limit(10).all()
    sentences_data = [sentence.serialize() for sentence in sentences]
    return jsonify(sentences_data)
