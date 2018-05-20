from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_get_passages(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Retrieve passages data
    res = app.get("/passages")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) > 0

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Try to retrieve passages data
    res = app.get("/passages")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1001

def test_not_authenticated(app):
    # Try to retrieve passages data
    res = app.get("/passages")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000
