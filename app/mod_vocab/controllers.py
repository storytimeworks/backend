from flask import Blueprint, jsonify, request

import json

from app import db
from app.mod_vocab.models import Entry, Sentence

mod_vocab = Blueprint("vocab", __name__, url_prefix="/vocabulary")

@mod_vocab.route("/entries", methods=["GET"])
def get_entries():
    query = "%" + request.args.get("q") + "%"

    entries = Entry.query.filter( \
        ((Entry.chinese.like(query) | Entry.pinyin.like(query)) & (Entry.source_is_chinese == True) | \
        (Entry.english.like(query) & (Entry.source_is_chinese == False))) \
    ).all()

    entries_data = [entry.serialize() for entry in entries]
    return jsonify(entries_data)

@mod_vocab.route("/entries/<entry_id>", methods=["GET"])
def get_entry_specific(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first()

    if entry is not None:
        return jsonify(entry.serialize())
    else:
        return jsonify(error=404, message="Entry not found."), 404

@mod_vocab.route("/entries", methods=["POST"])
def create_entry():
    chinese = request.json["chinese"]
    english = request.json["english"]
    pinyin = request.json["pinyin"]
    source_is_chinese = request.json["source_is_chinese"]

    entry = Entry(chinese, english, pinyin, source_is_chinese)
    db.session.add(entry)
    db.session.commit()

    return get_entry_specific(entry.id)

@mod_vocab.route("/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
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

    return get_entry_specific(entry_id)

@mod_vocab.route("/sentences")
def get_sentences():
    query = "%" + request.args.get("q") + "%"
    sentences = Sentence.query.filter(Sentence.chinese.like(query)).limit(10).all()
    sentences_data = [sentence.serialize() for sentence in sentences]
    return jsonify(sentences_data)
