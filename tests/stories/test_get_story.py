from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_get_story(app):
    # Retrieve a story
    res = app.get("/stories/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

def test_get_nonexistant_story(app):
    # Try to retrieve a story
    res = app.get("/stories/12340923")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1601
