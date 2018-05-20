from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_reset_password(app):
    # Test account username
    data = {
        "username": "user"
    }

    # Initiate a password reset for the test account
    res = app.post("/users/password/reset", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 204

def test_missing_parameters(app):
    # Try to initiate password reset without any data
    res = app.post("/users/password/reset")
    assert res.status_code == 400
