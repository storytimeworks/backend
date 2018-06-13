from flask import Blueprint, jsonify, request
import json, requests, uuid

from app import admin_required, db
from app.mod_nlp.models import NLPApp

mod_nlp = Blueprint("nlp", __name__, url_prefix="/nlp")

@mod_nlp.route("/<nlp_app_id>", methods=["GET"])
@admin_required
def get_nlp_app(nlp_app_id):
    app = NLPApp.query.filter_by(id=nlp_app_id).first()
    return jsonify(app.serialize())

@mod_nlp.route("", methods=["POST"])
@admin_required
def create_nlp_app():
    passage_id = request.json["passage_id"]

    name = "storytime-%d-%s" % (passage_id, str(uuid.uuid4())[0:8])

    response = requests.post(
        url="https://api.wit.ai/apps",
        params={
            "v": "20170307"
        },
        headers={
            "Authorization": "Bearer VKOYU7AADEZYXGN2BYIHKRKJZ7LTSCND",
            "Content-Type": "application/json; charset=utf-8"
        },
        data=json.dumps({
            "name": name,
            "lang": "zh",
            "private": True
        })
    )

    response_json = response.json()
    access_token = response_json["access_token"]
    app_id = response_json["app_id"]

    nlp_app = NLPApp(name, passage_id, access_token, app_id)
    db.session.add(nlp_app)
    db.session.commit()

    return get_nlp_app(nlp_app.id)

@mod_nlp.route("/<nlp_app_id>", methods=["DELETE"])
def delete_nlp_app(nlp_app_id):
    nlp_app = NLPApp.query.filter_by(id=nlp_app_id).first()

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

    NLPApp.query.filter_by(id=nlp_app_id).delete()
    db.session.commit()

    return ("", 204)
