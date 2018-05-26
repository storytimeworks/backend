from app import configure_test_client
from flask import Flask, session
import json, pytest, os, uuid

@pytest.fixture
def app():
    application = Flask(__name__)
    return configure_test_client(application)

def test_update_story(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Generate a random string to test with
    name = str(uuid.uuid4())[0:8]

    # Data to update this story with
    data = {
        "name": name
    }

    # Update this story on backend
    res = app.put("/stories/1", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] == 1
    assert data["name"] == name

def test_no_parameters(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Try to update this story without any parameters
    res = app.put("/stories/1")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1603

def test_not_authenticated(app):
    # Generate a random string to test with
    name = str(uuid.uuid4())[0:8]

    # Data to update this story with
    data = {
        "name": name
    }

    # Try to update this story on backend
    res = app.put("/stories/1", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Generate a random string to test with
    name = str(uuid.uuid4())[0:8]

    # Data to update this story with
    data = {
        "name": name
    }

    # Update this story on backend
    res = app.put("/stories/1", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1001

def test_nonexistant_story(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Generate a random string to test with
    name = str(uuid.uuid4())[0:8]

    # Data to update this story with
    data = {
        "name": name
    }

    # Update this story on backend
    res = app.put("/stories/123045", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 404
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1601
