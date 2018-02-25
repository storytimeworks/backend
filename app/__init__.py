from flask import redirect, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = None

def configure_app(app):
    global db

    app.config.from_object("config")

    cors = CORS(app)
    db = SQLAlchemy(app)

    from app.mod_vocab.controllers import mod_vocab as vocab_module
    from app.mod_users.controllers import mod_users as users_module

    app.register_blueprint(vocab_module)
    app.register_blueprint(users_module)

    if os.environ["ENVIRONMENT"] == "production":
        @app.before_request
        def before_request():
            if not request.is_secure:
                url = request.url.replace("http://", "https://", 1)
                code = 301
                return redirect(url, code=code)

    db.create_all()
