from app import configure_app
from flask import Flask, session
import json, pytest, os, uuid

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

def test_get_sentences(app):
    # Retrieve sentences with a given query
    res = app.get("/vocabulary/sentences?q=a")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) == 10

def test_no_query(app):
    # Retrieve sentences without any query
    res = app.get("/vocabulary/sentences")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) == 10
