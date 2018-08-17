from flask import Flask
from dotenv import load_dotenv
import os

from app import configure_app

if not "ENVIRONMENT" in os.environ:
    os.environ["ENVIRONMENT"] = "development"
    os.environ["FLASK_ENV"] = "development"
    os.environ["RDS_DB_NAME"] = "storytime"
    os.environ["RDS_HOSTNAME"] = "localhost"
    os.environ["RDS_PASSWORD"] = ""
    os.environ["RDS_USERNAME"] = "root"
    os.environ["SECRET_KEY"] = "secret"

    load_dotenv()

# Include application callable here so it can be used by WSGI
application = Flask(__name__)
configure_app(application)

# Run the application if it's being called by Elastic Beanstalk server
if __name__ == "__main__":
    is_production = os.environ["ENVIRONMENT"] == "production"
    application.run(debug=not is_production)
