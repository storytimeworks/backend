from app import configure_app
from flask import Flask, session
import json, pytest, os, uuid

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

def test_register_user(app):
    # Generate random username, with a in front so a letter is guaranteed first
    username = "a" + str(uuid.uuid4())[0:8]

    data = {
        "username": username,
        "email": username + "@email.com",
        "password": "my password is really long"
    }

    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] > 0

    # Ensure sensitive data is exposed since the user is now logged in
    assert "email" in data
    assert "settings" in data

def test_missing_parameters(app):
    # Try to register without passing data
    res = app.post("/users")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 104

def test_short_username(app):
    data = {
        "username": "abc",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a username that is too short
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the correct error is shown
    assert data["code"] == 105

def test_long_username(app):
    data = {
        "username": "abcdefghijklmnopq",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a username that is too long
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the correct error is shown
    assert data["code"] == 106

def test_dash_start_username(app):
    data = {
        "username": "-abcdef",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a username that starts with a dash
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 107

def test_underscore_start_username(app):
    data = {
        "username": "_abcdef",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a username that starts with an underscore
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 107

def test_invalid_character_username(app):
    data = {
        "username": "abcd$f",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a username that has an invalid character
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 108

def test_weak_password(app):
    data = {
        "username": "abcdef",
        "email": "testingabc@email.com",
        "password": "password123"
    }

    # Try to register with a weak password
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 109

def test_taken_username(app):
    data = {
        "username": "jack",
        "email": "testing@gmail.com",
        "password": "my password is really long"
    }

    # Try to register with a taken username
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 409
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 110

def test_used_email(app):
    data = {
        "username": "abcdef",
        "email": "testing@email.com",
        "password": "my password is really long"
    }

    # Try to register with a used email address
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 409
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 111

def test_invalid_email(app):
    data = {
        "username": "abcdef",
        "email": "asdf",
        "password": "my password is really long"
    }

    # Try to register with an invalid email address
    res = app.post("/users", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure that the correct error is shown
    assert data["code"] == 112
