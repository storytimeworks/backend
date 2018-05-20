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

def test_create_entry(app):
    # Be an admin for this test
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo",
        "source_is_chinese": True
    }

    # Create this entry on backend
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert data["id"] > 0
    assert data["chinese"] == "你好"
    assert data["english"] == "hello"
    assert data["pinyin"] == "nǐ hǎo"

def test_not_authenticated(app):
    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo",
        "source_is_chinese": True
    }

    # Try to create this entry without authentication
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 201

def test_normal_user(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Data for the 你好 vocabulary entry
    data = {
        "chinese": "你好",
        "english": "hello",
        "pinyin": "nǐ hǎo",
        "source_is_chinese": True
    }

    # Create this entry on backend
    res = app.post("/vocabulary/entries", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 401
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 201

def test_no_parameters(app):
    # Try to create an entry without passing parameters
    res = app.post("/vocabulary/entries")
    assert res.status_code == 400
    data = json.loads(res.data)

    # Ensure the error is correct
    assert data["code"] == 205