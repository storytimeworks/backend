from datetime import datetime
from flask import jsonify, redirect, request
from flask.json import JSONEncoder
import os

from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from raven.contrib.flask import Sentry

import email

db = None
sentry = None

def log_error(message):
    global sentry

    if os.environ["ENVIRONMENT"] == "production":
        sentry.captureMessage(message)

def configure_app(app):
    global db, sentry

    app.config.from_object("config")

    cors = CORS(app)
    db = SQLAlchemy(app)

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

    from app.mod_games.controllers import mod_games as games_module
    from app.mod_passages.controllers import mod_passages as passages_module
    from app.mod_speech.controllers import mod_speech as speech_module
    from app.mod_vocab.controllers import mod_vocab as vocab_module
    from app.mod_users.controllers import mod_users as users_module

    app.register_blueprint(games_module)
    app.register_blueprint(passages_module)
    app.register_blueprint(speech_module)
    app.register_blueprint(vocab_module)
    app.register_blueprint(users_module)

    app.json_encoder = StorytimeJSONEncoder

    db.create_all()

class StorytimeJSONEncoder(JSONEncoder):
    def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return JSONEncoder.default(self, obj)
