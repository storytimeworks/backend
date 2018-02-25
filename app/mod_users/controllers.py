from flask import Blueprint, jsonify, request, session

import bcrypt, json

from app import db
from app.mod_users.models import User

mod_users = Blueprint("users", __name__, url_prefix="/users")

@mod_users.route("/<user_id>", methods=["GET"])
def get_user_specific(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user is not None:
        return jsonify(user.serialize())
    else:
        return jsonify(error=404, message="User not found."), 404

@mod_users.route("", methods=["POST"])
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = bcrypt.hashpw(request.json["password"].encode("utf-8"), bcrypt.gensalt())

    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return get_user_specific(user.id)

@mod_users.route("/login", methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        session["user_id"] = user.id
        return ("", 204)
    else:
        return ("", 401)

@mod_users.route("/current", methods=["GET"])
def get_current_user():
    if "user_id" in session:
        return get_user_specific(session["user_id"])
    else:
        return ("", 401)

@mod_users.route("/current", methods=["DELETE"])
def logout():
    session.pop("user_id", None)
    return ("", 204)
