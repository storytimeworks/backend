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

def test_update_passage(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Generate a random string to test with
    english_name = str(uuid.uuid4())[0:8]

    # Data to update this passage with
    data = {
        "english_name": english_name
    }

    # Update this passage on backend
    res = app.put("/passages/3", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 3
    assert data["english_name"] == english_name

def test_no_parameters(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Try to update this passage without any parameters
    res = app.put("/passages/3")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 505

def test_not_authenticated(app):
    # Generate a random string to test with
    english_name = str(uuid.uuid4())[0:8]

    # Data to update this passage with
    data = {
        "english_name": english_name
    }

    # Try to update this passage on backend
    res = app.put("/passages/3", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Generate a random string to test with
    english_name = str(uuid.uuid4())[0:8]

    # Data to update this passage with
    data = {
        "english_name": english_name
    }

    # Update this passage on backend
    res = app.put("/passages/3", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 502

def test_nonexistant_passage(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Generate a random string to test with
    english_name = str(uuid.uuid4())[0:8]

    # Data to update this passage with
    data = {
        "english_name": english_name
    }

    # Update this passage on backend
    res = app.put("/passages/123045", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 503
