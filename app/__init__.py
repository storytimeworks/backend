from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config.from_object("config")

cors = CORS(application)
db = SQLAlchemy(application)

from app.mod_vocab.controllers import mod_vocab as vocab_module
application.register_blueprint(vocab_module)

db.create_all()
