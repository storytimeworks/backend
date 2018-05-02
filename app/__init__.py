from datetime import datetime
from flask import redirect, request
from flask.json import JSONEncoder
import os

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from raven.contrib.flask import Sentry

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

    from app.mod_passages.controllers import mod_passages as passages_module
    from app.mod_speech.controllers import mod_speech as speech_module
    from app.mod_vocab.controllers import mod_vocab as vocab_module
    from app.mod_users.controllers import mod_users as users_module

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
