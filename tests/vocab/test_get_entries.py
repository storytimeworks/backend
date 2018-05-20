from app import configure_test_client
from flask import Flask, session
import json, pytest, os

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_get_entries(app):
    # Retrieve entries data
    res = app.get("/vocabulary/entries")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) > 0
