from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_create_story(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Data for the first story
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader."
    }

    # Create a story
    res = app.post("/stories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["chinese_name"] == "你好"
    assert data["english_name"] == "Hello"
    assert data["description"] == "Sarah introduces herself to the reader."
    assert data["passage_ids"] == []

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Data for the first story
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader.",
        "story_id": 1
    }

    # Try to create a story
    res = app.post("/stories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1001

def test_missing_authentication(app):
    # Data for the first story
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader.",
        "story_id": 1
    }

    # Try to create a story
    res = app.post("/stories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_missing_parameters(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Try to create a story
    res = app.post("/stories")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1602
