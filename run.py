from flask import Flask
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
    os.environ["SENTRY_DSN"] = "https://80e67f6e6518406d847acd07ef2bb0bb:51e96f1b19d24198ab8c8d8cc4ebd9f9@sentry.io/294045"
    os.environ["WIT_ACCESS_TOKEN"] = "IHJZTZVGYBNCPBNNZDHNJYVJ4M4NYP4B"

# Include application callable here so it can be used by WSGI
application = Flask(__name__)
configure_app(application)

# Run the application if it's being called by Elastic Beanstalk server
if __name__ == "__main__":
    from app import socket

    is_production = os.environ["ENVIRONMENT"] == "production"
    socket.run(application, debug=not is_production)
