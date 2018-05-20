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

def test_create_passage(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Data for the first passage
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader.",
        "story_id": 1
    }

    # Create a passage
    res = app.post("/passages", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["chinese_name"] == "你好"
    assert data["english_name"] == "Hello"
    assert data["description"] == "Sarah introduces herself to the reader."
    assert data["story_id"] == 1

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Data for the first passage
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader.",
        "story_id": 1
    }

    # Try to create a passage
    res = app.post("/passages", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 403
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 502

def test_missing_authentication(app):
    # Data for the first passage
    data = {
        "chinese_name": "你好",
        "english_name": "Hello",
        "description": "Sarah introduces herself to the reader.",
        "story_id": 1
    }

    # Try to create a passage
    res = app.post("/passages", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 1000

def test_missing_parameters(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Try to create a passage
    res = app.post("/passages")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 504
