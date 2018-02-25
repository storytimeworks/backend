from flask import Blueprint, jsonify, request, session

import bcrypt, json, re, validators
from zxcvbn import zxcvbn

from app import db
import app.mod_users.errors as errors
from app.mod_users.models import User

mod_users = Blueprint("users", __name__, url_prefix="/users")

@mod_users.route("/<user_id>", methods=["GET"])
def get_user_specific(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user is not None:
        return jsonify(user.serialize())
    else:
        return errors.user_not_found()

@mod_users.route("", methods=["POST"])
def register():
    if "username" not in request.json or "email" not in request.json or "password" not in request.json:
        return errors.missing_registration_parameters()

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(username) < 4:
        return errors.short_username()
    elif len(username) > 16:
        return errors.long_username()
    elif username[0] == "-" or username[0] == "_":
        return errors.no_dash_start_username()
    elif re.match("^[\w-]+$", username) is None:
        return errors.invalid_username()

    password_strength = zxcvbn(password, user_inputs=[username, email])
    if password_strength["score"] < 2:
        return errors.weak_password(password_strength["feedback"])

    if User.query.filter_by(username=username).count() > 0:
        return errors.username_taken()
    elif User.query.filter_by(email=email).count() > 0:
        return errors.email_used()

    if not validators.email(email):
        return errors.invalid_email()

    hashed_password = bcrypt.hashpw(request.json["password"].encode("utf-8"), bcrypt.gensalt())

    user = User(username, email, hashed_password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return get_user_specific(user.id)

@mod_users.route("/login", methods=["POST"])
def login():
    if "email" not in request.json or "password" not in request.json:
        return errors.missing_login_parameters()

    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    password_is_correct = bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))

    if user and password_is_correct:
        session["user_id"] = user.id
        return get_user_specific(user.id)
    else:
        return errors.invalid_credentials()

@mod_users.route("/current", methods=["GET"])
def get_current_user():
    if "user_id" in session:
        return get_user_specific(session["user_id"])
    else:
        return errors.missing_authentication()

@mod_users.route("/current", methods=["DELETE"])
def logout():
    session.pop("user_id", None)
    return ("", 204)
