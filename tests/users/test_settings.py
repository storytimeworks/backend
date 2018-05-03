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

def test_set_settings(app):
    # Be a normal user for this test
    with app.session_transaction() as session:
        session["user_id"] = 2

    # Generate random "names" to test with
    first_name = str(uuid.uuid4())[0:8]
    last_name = str(uuid.uuid4())[0:8]

    data = {
        "section": "profile",
        "data": {
            "first_name": first_name,
            "last_name": last_name
        }
    }

    # Set the first and last names in settings
    res = app.put("/users/2", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure that the names were set correctly
    assert data["settings"]["profile"]["first_name"] == first_name
    assert data["settings"]["profile"]["last_name"] == last_name
