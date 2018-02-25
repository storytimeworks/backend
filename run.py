from flask import Flask
import os

from app import configure_app

# Include application callable here so it can be used by WSGI
application = Flask(__name__)
configure_app(application)

# Run the application if it's being called by Elastic Beanstalk server
if __name__ == "__main__":
    is_production = os.environ["ENVIRONMENT"] == "production"
    application.run(debug=not is_production)
