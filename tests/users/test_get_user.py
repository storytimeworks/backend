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

def test_get_user(app):
    # Retrieve user data
    res = app.get("/users/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

    # Ensure sensitive data is not being exposed
    assert "email" not in data
    assert "settings" not in data

def test_get_nonexistant_user(app):
    # Retrieve data for a user that doesn't exist
    res = app.get("/users/0")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the correct error is being shown
    assert data["code"] == 103

def test_get_authenticated_user(app):
    # Set the user id for this session
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Retrieve data for the currently authenticated user
    res = app.get("/users/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

    # Ensure sensitive data is shown when logged in
    assert "email" in data
    assert "settings" in data

def test_get_user_when_logged_in(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Retrieve data for a different user
    res = app.get("/users/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

    # Ensure sensitive data is not shown to normal users
    assert "email" not in data
    assert "settings" not in data

def test_get_user_as_admin(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Retrieve data for a different user
    res = app.get("/users/2")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 2

    # Ensure sensitive data is shown to admins
    assert "email" in data
    assert "settings" in data
