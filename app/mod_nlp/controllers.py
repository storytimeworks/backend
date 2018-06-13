from flask import Blueprint, jsonify, request
import json, os, requests, uuid

from app import admin_required, db
from app.mod_nlp import check_body
import app.mod_nlp.errors as errors
from app.mod_nlp.models import NLPApp

mod_nlp = Blueprint("nlp", __name__, url_prefix="/nlp")

@mod_nlp.route("/<nlp_app_id>", methods=["GET"])
@admin_required
def get_nlp_app(nlp_app_id):
    """Retrieves data about an NLP app.

    Parameters:
        nlp_app_id: The id of the app being retrieved.

    Returns:
        JSON data about the app with this id.
    """

    # Retrieve the app with this id
    app = NLPApp.query.filter_by(id=nlp_app_id).first()

    if app:
        # Return data about this app if it exists
        return jsonify(app.serialize())
    else:
        # Otherwise, return 404
        return errors.app_not_found()

@mod_nlp.route("", methods=["POST"])
@admin_required
def create_nlp_app():
    """Creates an NLP app for a specified passage.

    Arguments:
        passage_id: The id of the passage that this app corresponds to.

    Returns:
        JSON data about the app that was just created.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["passage_id"]):
        return errors.missing_create_app_parameters()

    passage_id = request.json["passage_id"]

    # Create the name for this NLP app
    name = "storytime-%d-%s" % (passage_id, str(uuid.uuid4())[0:8])

    # Create this app on Wit.ai
    response = requests.post(
        url="https://api.wit.ai/apps",
        params={
            "v": "20170307"
        },
        headers={
            "Authorization": "Bearer %s" % os.environ["WIT_ACCESS_TOKEN"],
            "Content-Type": "application/json; charset=utf-8"
        },
        data=json.dumps({
            "name": name,
            "lang": "zh",
            "private": True
        })
    )

    # Retrieve data given back to us by Wit.ai
    response_json = response.json()
    access_token = response_json["access_token"]
    app_id = response_json["app_id"]

    # Create this app in the database
    nlp_app = NLPApp(name, passage_id, access_token, app_id)
    db.session.add(nlp_app)
    db.session.commit()

    # Return JSON data about this app
    return get_nlp_app(nlp_app.id)

@mod_nlp.route("/<nlp_app_id>", methods=["DELETE"])
def delete_nlp_app(nlp_app_id):
    """Deletes the NLP app with this id.

    Parameters:
        nlp_app_id: The id of the NLP app that needs to be deleted.

    Returns:
        204 no content.
    """

    # Find the app that's being deleted
    nlp_app = NLPApp.query.filter_by(id=nlp_app_id).first()

    # Return 404 if no app exists with this id
    if not nlp_app:
        return errors.app_not_found()

    # Delete this app on Wit.ai before deleting it locally
    response = requests.delete(
        url="https://api.wit.ai/apps/%s" % nlp_app.app_id,
        params={
            "v": "20170307"
        },
        headers={
            "Authorization": "Bearer %s" % nlp_app.access_token,
            "Content-Type": "application/json; charset=utf-8"
        }
    )

    # Now, delete this app from the database
    NLPApp.query.filter_by(id=nlp_app_id).delete()
    db.session.commit()

    return ("", 204)
