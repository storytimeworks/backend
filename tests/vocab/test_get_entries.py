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

def test_get_entries(app):
    # Retrieve entries data
    res = app.get("/vocabulary/entries")
    assert res.status_code == 200
    data = json.loads(res.data)

    # Ensure the response is correct
    assert len(data) > 0
