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

def test_get_entries_health(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Retrieve vocab health data
    res = app.get("/vocabulary/health")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert "data" in data.keys()
    assert "no_translations" in data.keys()

def test_no_authentication(app):
    # Try to retrieve vocab health data without authentication
    res = app.get("/vocabulary/health")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_not_authorized(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Try to retrieve vocab health data as a normal user
    res = app.get("/vocabulary/health")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 202
