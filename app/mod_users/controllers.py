from flask import Blueprint, jsonify, request, session

import bcrypt, json

from app import db
from app.mod_users.models import User

mod_users = Blueprint("users", __name__, url_prefix="/users")

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
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()

    if user is not None:
        return jsonify(user.serialize())
    else:
        return ("", 401)

@mod_users.route("/current", methods=["DELETE"])
def logout():
    session.clear()
    return ("", 204)
