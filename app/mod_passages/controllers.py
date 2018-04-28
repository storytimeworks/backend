from flask import Blueprint, jsonify, request, session
import json

from app import db
from app.mod_passages.models import Passage
from app.mod_users.models import User

mod_passages = Blueprint("passages", __name__, url_prefix="/passages")

@mod_passages.route("", methods=["GET"])
def get_passages():
    passages = Passage.query.all()
    passages_data = [passage.serialize() for passage in passages]
    return jsonify(passages_data)

@mod_passages.route("/<passage_id>", methods=["GET"])
def get_passage_specific(passage_id):
    passage = Passage.query.filter_by(id=passage_id).first()

    if passage is not None:
        return jsonify(passage.serialize())
    else:
        return jsonify(error=404, message="Passage not found."), 404

@mod_passages.route("", methods=["POST"])
def create_passage():
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

    name = request.json["name"]
    story_id = request.json["story_id"]
    data = json.dumps(request.json["data"])

    passage = Passage(name, story_id, data)
    db.session.add(passage)
    db.session.commit()

    return get_passage_specific(passage.id)

@mod_passages.route("/<passage_id>", methods=["PUT"])
def update_passage(passage_id):
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

    passage = Passage.query.filter_by(id=passage_id).first()

    if key == "name":
        passage.name = value
    elif key == "data":
        passage.data = json.dumps(value)

    db.session.commit()

    return get_passage_specific(passage_id)
