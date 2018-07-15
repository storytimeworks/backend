from flask import Blueprint, jsonify, request
from flask_login import login_required
from pypinyin import pinyin

import json

from app import admin_required, db
from app.mod_games.mod_compound.models import CompoundQuestion
from app.utils import check_body

mod_compound_game = Blueprint("compound_game", __name__, url_prefix="/games/compound")

@mod_compound_game.route("/play", methods=["GET"])
@login_required
def play_game():
    questions = CompoundQuestion.query.order_by(db.func.random()).limit(10).all()
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_compound_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    questions = CompoundQuestion.query.all()
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_compound_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    question = CompoundQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_compound_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    if not check_body(request, ["prompt", "choices"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"]
    choices = request.json["choices"]

    question = CompoundQuestion(prompt, choices)
    db.session.add(question)
    db.session.commit()

    return jsonify(question.serialize())

@mod_compound_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    key = None
    value = None

    if request.json and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_question_parameters()

    question = CompoundQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()

    if key == "choices":
        print(request.json)
        question.choices = json.dumps(value)

        pinyin_choices = value

        for idx, choice in enumerate(pinyin_choices):
            for jdx, option in enumerate(choice):
                pinyin_choices[idx][jdx] = pinyin(option)[0][0]

        question.pinyin_choices = json.dumps(pinyin_choices)
    elif key == "prompt":
        question.prompt = value

    db.session.commit()

    return jsonify(question.serialize())
