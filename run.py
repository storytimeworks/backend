from flask import Flask
from app import configure_app

# Include application callable here so it can be used by WSGI
application = Flask(__name__)
configure_app(application)

# Run the application if it's being called by Elastic Beanstalk server
if __name__ == "__main__":
    application.run(debug=True)
