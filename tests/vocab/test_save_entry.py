from app import configure_test_client
from flask import Flask, session
import json, pytest, os, uuid

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_save_entry(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Save the entry with id = 1
    res = app.post("/vocabulary/entries/1/save")
    assert res.status_code == 204

    # Check to make sure the entry was saved
    res = app.get("/users/2")
    assert res.status_code == 200

    data = json.loads(res.data)
    assert 1 in data["saved_entry_ids"]

def test_not_authenticated(app):
    # Try to save an entry
    res = app.post("/vocabulary/entries/2/save")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000
