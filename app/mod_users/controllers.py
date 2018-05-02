from flask import Blueprint, jsonify, request, session

import bcrypt, json, re, validators
from zxcvbn import zxcvbn

from app import db, log_error
import app.mod_users.errors as errors
from app.mod_users.models import User

mod_users = Blueprint("users", __name__, url_prefix="/users")

@mod_users.route("/<user_id>", methods=["GET"])
def get_user_specific(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return errors.user_not_found()

    full = False

    if "user_id" in session:
        session_user_id = session["user_id"]
        session_user = User.query.filter_by(id=session_user_id).first()

        if session_user_id == user_id or 1 in json.loads(session_user.groups):
            full = True

    return jsonify(user.serialize(full))

@mod_users.route("", methods=["POST"])
def register():
    if request.json == None or "username" not in request.json or "email" not in request.json or "password" not in request.json:
        return errors.missing_registration_parameters()

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    # zxcvbn throws an error if password is empty string, so catch this early
    if len(password) == 0:
        return errors.missing_registration_parameters()

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

@mod_users.route("/<user_id>", methods=["PUT"])
def update_user_specific(user_id):
    if "user_id" not in session:
        return errors.missing_authentication()

    if request.json == None or "section" not in request.json or "data" not in request.json:
        return errors.missing_update_parameters()

    section = request.json["section"]
    data = request.json["data"]

    user = User.query.filter_by(id=user_id).first()

    session_user_id = session["user_id"]
    session_user = User.query.filter_by(id=session_user_id).first()

    if not user:
        return errors.user_not_found()
    elif not session_user:
        log_error("Session user does not exist, something is wrong")
        return errors.missing_authentication()
    elif user_id != session_user_id and 1 not in json.loads(session_user.groups):
        # Only the authenticated user and admins can update a user's settings
        return errors.not_authorized()

    settings = user.get_settings()

    if section not in settings:
        return errors.invalid_settings_section()
    elif section == "profile":
        user.username = data["username"]
        user.email = data["email"]

        settings[section] = {
            "first_name": data["first_name"],
            "last_name": data["last_name"]
        }
    else:
        settings[section] = data

    user.settings = json.dumps(settings)

    db.session.commit()

    return get_user_specific(user.id)

@mod_users.route("/login", methods=["POST"])
def login():
    if request.json == None or "username" not in request.json or "password" not in request.json:
        return errors.missing_login_parameters()

    username = request.json["username"]
    password = request.json["password"]

    # Allow login with username or email
    user = User.query.filter((User.username == username) | (User.email == username)).first()

    if user == None:
        return errors.invalid_credentials()

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
    session.clear()
    return ("", 204)
