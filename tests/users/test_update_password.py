from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_update_password(app):
    # Set the user id for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Configure data for switching to a new password
    data = {
        "current_password": "this is my password",
        "new_password": "this is my temporary password"
    }

    # Switch to the new password
    res = app.put("/users/2/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 2

    # Set data for switching back to the old password
    data = {
        "current_password": "this is my temporary password",
        "new_password": "this is my password"
    }

    # Switch back to the old password so this account can still be used for testing
    res = app.put("/users/2/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 2

def test_missing_parameters(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Try to switch passwords without sending any data
    res = app.put("/users/2/password")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1117

def test_not_logged_in(app):
    data = {
        "current_password": "this is my password",
        "new_password": "this is my temporary password"
    }

    # Try to switch passwords without being logged in
    res = app.put("/users/2/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_nonexistant_user(app):
    with app.session_transaction() as session:
        session["user_id"] = 1

    data = {
        "current_password": "this is my password",
        "new_password": "this is my temporary password"
    }

    # Try to set new password for a user that doesn't exist
    res = app.put("/users/13545/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1103

def test_not_authorized(app):
    # Set user id to a normal user
    with app.session_transaction() as session:
        session["user_id"] = 2

    data = {
        "current_password": "this is my password",
        "new_password": "this is my temporary password"
    }

    # Try to set someone else's password
    res = app.put("/users/1/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1115

def test_incorrect_password(app):
    # Set user id to the test account
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Set current password to be incorrect
    data = {
        "current_password": "password",
        "new_password": "this is my temporary password"
    }

    # Try to set the incorrect password
    res = app.put("/users/2/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1118

def test_weak_password(app):
    # Set user id to the test account
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Set new password to be very weak
    data = {
        "current_password": "this is my password",
        "new_password": "password123"
    }

    # Try to set the weak password
    res = app.put("/users/2/password", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1109
