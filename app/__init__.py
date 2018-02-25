from flask import redirect, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
import os

db = None

def configure_app(app):
    global db

    app.config.from_object("config")

    cors = CORS(app)
    db = SQLAlchemy(app)
    sslify = SSLify(app, permanent=True)

    from app.mod_vocab.controllers import mod_vocab as vocab_module
    from app.mod_users.controllers import mod_users as users_module

    app.register_blueprint(vocab_module)
    app.register_blueprint(users_module)

    db.create_all()
