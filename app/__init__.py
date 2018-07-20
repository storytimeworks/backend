from datetime import datetime
from flask import current_app, jsonify, redirect, request
from flask.json import JSONEncoder
from functools import wraps
import os

from flask_cors import CORS
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from raven.contrib.flask import Sentry

import email

db = None
sentry = None

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin:
            data = {
                "code": 1001,
                "message": "You don't have permission to perform this action"
            }

            return jsonify(data), 403
        return func(*args, **kwargs)

    return decorated_view

def log_error(message):
    global sentry

    if os.environ["ENVIRONMENT"] == "production":
        sentry.captureMessage(message)

def configure_app(app):
    global db, sentry

    app.config.from_object("config")

    cors = CORS(app)
    db = SQLAlchemy(app)

    app.config["SENTRY_CONFIG"] = {
        "environment": os.environ["ENVIRONMENT"]
    }

    if os.environ["ENVIRONMENT"] == "production":
        # Only use Sentry and SSL in production
        sentry = Sentry(app)
        sslify = SSLify(app, permanent=True)

    # Set up login manager here
    from app.mod_users.models import User

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        data = {
            "code": 1000,
            "message": "You are unauthorized to perform this action"
        }

        return jsonify(data), 401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    from app.mod_characters.controllers import mod_characters as characters_module
    from app.mod_games.controllers import mod_games as games_module
    from app.mod_games.mod_compound.controllers import mod_compound_game as compound_game_module
    from app.mod_games.mod_expressions.controllers import mod_expressions_game as expressions_game_module
    from app.mod_games.mod_mad_minute.controllers import mod_mad_minute_game as mad_minute_game_module
    from app.mod_games.mod_scribe.controllers import mod_scribe_game as scribe_game_module
    from app.mod_games.mod_speaker.controllers import mod_speaker_game as speaker_game_module
    from app.mod_games.mod_writer.controllers import mod_writer_game as writer_game_module
    from app.mod_mastery.controllers import mod_mastery as mastery_module
    from app.mod_nlp.controllers import mod_nlp as nlp_module
    from app.mod_passages.controllers import mod_passages as passages_module
    from app.mod_path.controllers import mod_path as path_module
    from app.mod_speech.controllers import mod_speech as speech_module
    from app.mod_stories.controllers import mod_stories as stories_module
    from app.mod_vocab.controllers import mod_vocab as vocab_module
    from app.mod_users.controllers import mod_users as users_module

    app.register_blueprint(characters_module)
    app.register_blueprint(games_module)
    app.register_blueprint(compound_game_module)
    app.register_blueprint(expressions_game_module)
    app.register_blueprint(mad_minute_game_module)
    app.register_blueprint(scribe_game_module)
    app.register_blueprint(speaker_game_module)
    app.register_blueprint(writer_game_module)
    app.register_blueprint(mastery_module)
    app.register_blueprint(nlp_module)
    app.register_blueprint(passages_module)
    app.register_blueprint(path_module)
    app.register_blueprint(speech_module)
    app.register_blueprint(stories_module)
    app.register_blueprint(vocab_module)
    app.register_blueprint(users_module)

    app.json_encoder = StorytimeJSONEncoder

    from app.log import Log

    @app.after_request
    def after_request(response):
        ip = None

        if os.environ["ENVIRONMENT"] == "production":
            ip = request.headers.get("X-Forwarded-For")
        else:
            ip = request.remote_addr

        method = request.method
        path = request.path
        status_code = response.status_code
        user_id = None

        if current_user.is_authenticated:
            user_id = current_user.id

        log = Log(ip, method, path, status_code, user_id)
        db.session.add(log)
        db.session.commit()

        return response

    db.create_all()

def configure_test_client(application):
    os.environ["ENVIRONMENT"] = "development"
    os.environ["RDS_DB_NAME"] = "storytime_test"
    os.environ["RDS_HOSTNAME"] = "localhost"
    os.environ["RDS_PASSWORD"] = ""
    os.environ["RDS_USERNAME"] = "root"
    os.environ["SECRET_KEY"] = "secret"

    configure_app(application)
    application.debug = True
    return application.test_client()

class StorytimeJSONEncoder(JSONEncoder):
    def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return JSONEncoder.default(self, obj)
