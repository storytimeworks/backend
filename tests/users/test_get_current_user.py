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

def test_current_user(app):
    # Set the user id for this session
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Retrieve data about the current user
    res = app.get("/users/current")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

    # Ensure sensitive data is shown when logged in
    assert "email" in data
    assert "settings" in data

def test_not_authenticated(app):
    # Retrieve data about nobody
    res = app.get("/users/current")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 102
