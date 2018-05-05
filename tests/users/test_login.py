from app import configure_app
from flask import Flask
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

def test_login(app):
    # Credentials for the test account
    data = {
        "username": "hello",
        "password": "this is my password"
    }

    # Log in with these credentials
    res = app.post("/users/login", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the returned data is correct
    assert data["id"] == 2

def test_login_with_email(app):
    # Credentials for the test account
    data = {
        "username": "test@test.com",
        "password": "this is my password"
    }

    # Log in with these credentials
    res = app.post("/users/login", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the returned data is correct
    assert data["id"] == 2

def test_missing_parameters(app):
    # Try to log in without passing data
    res = app.post("/users/login")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 113

def test_incorrect_password(app):
    # Credentials for the test account, with the wrong password
    data = {
        "username": "hello",
        "password": "hello"
    }

    # Try to log in with these credentials
    res = app.post("/users/login", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 101

def test_nonexistant_user(app):
    # Credentials for an account that doesn't exist
    data = {
        "username": "nonexistant_user",
        "password": "this is my password"
    }

    # Try to log in with these credentials
    res = app.post("/users/login", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 101
