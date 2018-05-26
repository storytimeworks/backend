# from app import configure_test_client
# from flask import Flask, session
# import json, pytest, os, uuid
#
# @pytest.fixture
# def app():
#     application = Flask(__name__)
#     return configure_test_client(application)
#
# def test_register_user(app):
#     # Generate random username, with a in front so a letter is guaranteed first
#     username = "a" + str(uuid.uuid4())[0:8]
#
#     data = {
#         "username": username,
#         "email": username + "@email.com",
#         "password": "my password is really long"
#     }
#
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 200
#     data = json.loads(res.data)
#
#     # Ensure the response is correct
#     assert data["id"] > 0
#
#     # Ensure sensitive data is exposed since the user is now logged in
#     assert "email" in data
#     assert "settings" in data
#
# def test_missing_parameters(app):
#     # Try to register without passing data
#     res = app.post("/users")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure the error is correct
#     assert data["code"] == 1104
#
# def test_short_username(app):
#     data = {
#         "username": "abc",
#         "email": "testing@email.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a username that is too short
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure the correct error is shown
#     assert data["code"] == 1105
#
# def test_long_username(app):
#     data = {
#         "username": "abcdefghijklmnopq",
#         "email": "testing@email.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a username that is too long
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure the correct error is shown
#     assert data["code"] == 1106
#
# def test_dash_start_username(app):
#     data = {
#         "username": "-abcdef",
#         "email": "testing@email.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a username that starts with a dash
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1107
#
# def test_underscore_start_username(app):
#     data = {
#         "username": "_abcdef",
#         "email": "testing@email.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a username that starts with an underscore
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1107
#
# def test_invalid_character_username(app):
#     data = {
#         "username": "abcd$f",
#         "email": "testing@email.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a username that has an invalid character
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1108
#
# def test_weak_password(app):
#     data = {
#         "username": "abcdef",
#         "email": "testingabc@email.com",
#         "password": "password123"
#     }
#
#     # Try to register with a weak password
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1109
#
# def test_taken_username(app):
#     data = {
#         "username": "user",
#         "email": "testing@gmail.com",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a taken username
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 409
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1110
#
# def test_used_email(app):
#     data = {
#         "username": "abcdef",
#         "email": "user@storytime.works",
#         "password": "my password is really long"
#     }
#
#     # Try to register with a used email address
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 409
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1111
#
# def test_invalid_email(app):
#     data = {
#         "username": "abcdefgh",
#         "email": "asdf",
#         "password": "my password is really long"
#     }
#
#     # Try to register with an invalid email address
#     res = app.post("/users", data=json.dumps(data), content_type="application/json")
#     assert res.status_code == 400
#     data = json.loads(res.data)
#
#     # Ensure that the correct error is shown
#     assert data["code"] == 1112
