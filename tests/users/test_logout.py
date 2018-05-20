from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_logout(app):
    # Set the user id for this session
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Log out the user
    res = app.delete("/users/current")
    assert res.status_code == 204

    # Ensure the session has been cleared
    with app.session_transaction() as session:
        assert "user_id" not in session
