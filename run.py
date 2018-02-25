from flask import Flask
from app import configure_app

application = Flask(__name__)
configure_app(application)

if __name__ == "__main__":
    application.run(debug=True)
