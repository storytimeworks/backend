from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

import random
from shushu import convert

from app import db
from app.mod_games.models import GameResult
from app.mod_games.mod_mad_minute import check_body
from app.mod_games.mod_mad_minute.models import MadMinuteResult
from app.pinyin import pinyin

mod_mad_minute_game = Blueprint("mad_minute_game", __name__, url_prefix="/games/mad_minute")

@mod_mad_minute_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 30 questions in order to play a game.

    Returns:
        JSON data for all of the questions.
    """

    questions = []

    for _ in range(30):
        first_number = 5
        second_number = 10

        answer = ""
        prompt = ""

        addition = random.randint(0, 1) == 0

        if addition:
            while first_number + second_number > 10:
                first_number = random.randint(1, 10)
                second_number = random.randint(1, 10)

            answer = convert(first_number + second_number)
            prompt = pinyin(convert(first_number)) + " + " + pinyin(convert(second_number)) + " ="
        else:
            while first_number - second_number < 1:
                first_number = random.randint(1, 10)
                second_number = random.randint(1, 10)

            answer = convert(first_number - second_number)
            prompt = pinyin(convert(first_number)) + " - " + pinyin(convert(second_number)) + " ="

        question = {
            "prompt": prompt.lower(),
            "answer": answer,
            "answer_pinyin": pinyin(answer).lower()
        }

        questions.append(question)

    return jsonify(questions)

@mod_mad_minute_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game, storing any necessary data.

    Returns:
        JSON data of the completed game.
    """

    if not check_body(request, ["correct", "wrong"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    wrong = request.json["wrong"]

    result = GameResult(current_user.id, 1, 0)
    db.session.add(result)
    db.session.flush()

    mad_minute_result = MadMinuteResult(current_user.id, result.id, correct, wrong)
    db.session.add(mad_minute_result)
    db.session.commit()

    return jsonify(result.serialize())
