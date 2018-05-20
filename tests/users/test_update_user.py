from app import configure_test_client
from flask import Flask, session
import json, pytest, os, uuid

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_set_settings(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Generate random "names" to test with
    first_name = str(uuid.uuid4())[0:8]
    last_name = str(uuid.uuid4())[0:8]

    data = {
        "section": "profile",
        "data": {
            "first_name": first_name,
            "last_name": last_name,
            "username": "hello",
            "email": "test@test.com"
        }
    }

    # Set the first and last names in settings
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure that the names were set correctly
    assert data["settings"]["profile"]["first_name"] == first_name
    assert data["settings"]["profile"]["last_name"] == last_name

def test_missing_parameters(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Try to set settings without passing data
    res = app.put("/users/2")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1114

def test_not_authenticated(app):
    # Create generic profile data to test with
    data = {
        "section": "profile",
        "data": {
            "first_name": "John",
            "last_name": "Smith"
        }
    }

    # Try to set the first and last names in settings
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_nonexistant_user(app):
    # Be an admin, who can change a different user's settings
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Create generic profile data to test with
    data = {
        "section": "profile",
        "data": {
            "first_name": "John",
            "last_name": "Smith"
        }
    }

    # Try to set the first and last names in settings
    res = app.put("/users/12094", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1103

def test_not_authorized(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Create generic profile data to test with
    data = {
        "section": "profile",
        "data": {
            "first_name": "John",
            "last_name": "Smith"
        }
    }

    # Try to set the first and last names for a different user in settings
    res = app.put("/users/1", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1115

def test_invalid_setting(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Create data for a nonexistant section
    data = {
        "section": "something",
        "data": {
            "key": "value"
        }
    }

    # Try to set data for an invalid section
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1116

def test_invalid_username(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Create profile data with an invalid username
    data = {
        "section": "profile",
        "data": {
            "first_name": "John",
            "last_name": "Smith",
            "username": "-asdf"
        }
    }

    # Try setting the invalid username in settings
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1107

def test_invalid_email(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Create profile data with an invalid email address
    data = {
        "section": "profile",
        "data": {
            "first_name": "John",
            "last_name": "Smith",
            "email": "asdf"
        }
    }

    # Try setting the invalid email address in settings
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1112
