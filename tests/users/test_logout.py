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

def test_logout(app):
    # Set the user id for this session
    with app.session_transaction() as session:
        session["user_id"] = 1

    # Log out the user
    res = app.delete("/users/current")
    assert res.status_code == 204

    # Ensure the session has been cleared
    with app.session_transaction() as session:
        assert "user_id" not in session
