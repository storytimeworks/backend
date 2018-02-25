from flask import Flask
from app import configure_app

application = Flask(__name__)
configure_app(application)

application.run(debug=True)
