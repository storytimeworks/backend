from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_get_entry(app):
    # Retrieve entry data
    res = app.get("/vocabulary/entries/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

def test_get_nonexistant_entry(app):
    # Try to retrieve entry data
    res = app.get("/vocabulary/entries/1039853")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the correct error is being shown
    assert data["code"] == 1204
