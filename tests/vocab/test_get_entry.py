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

def test_get_entry(app):
    # Retrieve entry data
    res = app.get("/vocabulary/entries/1")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1

def test_get_nonexistant_entry(app):
    # Try to retrieve entry data
    res = app.get("/vocabulary/entries/2039853")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the correct error is being shown
    assert data["code"] == 204
