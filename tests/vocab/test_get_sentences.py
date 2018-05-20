from app import configure_test_client
from flask import Flask, session
import json, pytest, os, uuid

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_get_sentences(app):
    # Retrieve sentences with a given query
    res = app.get("/vocabulary/sentences?q=a")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) == 0

def test_no_query(app):
    # Retrieve sentences without any query
    res = app.get("/vocabulary/sentences")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) == 0
