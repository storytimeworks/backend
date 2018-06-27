from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.pinyin import pinyin
import random
from shushu import convert

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
