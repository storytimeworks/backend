from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_create_entry(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo"
    }

    # Create this entry on backend
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] > 0
    assert data["chinese"] == "你好"
    assert data["english"] == "hello"
    assert data["pinyin"] == "nǐ hǎo"

def test_not_authenticated(app):
    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo"
    }

    # Try to create this entry without authentication
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo"
    }

    # Create this entry on backend
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1001

def test_no_parameters(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Try to create an entry without passing parameters
    res = app.post("/vocabulary/entries")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1205
