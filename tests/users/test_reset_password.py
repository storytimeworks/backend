from app import configure_app
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    os.environ["ENVIRONMENT"] = "dev"
    os.environ["RDS_DB_NAME"] = "storytime"
    os.environ["RDS_HOSTNAME"] = "localhost"
    os.environ["RDS_PASSWORD"] = ""
    os.environ["RDS_USERNAME"] = "root"
    os.environ["SECRET_KEY"] = "secret"

    application = Flask(__name__)
    configure_app(application)
    application.debug = True
    return application.test_client()

def test_reset_password(app):
    # Test account username
    data = {
        "username": "hello"
    }

    # Initiate a password reset for the test account
    res = app.post("/users/password/reset", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 204

def test_missing_parameters(app):
    # Try to initiate password reset without any data
    res = app.post("/users/password/reset")
    assert res.status_code == 400
