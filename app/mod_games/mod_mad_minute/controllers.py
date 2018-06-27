from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.pinyin import pinyin
import random

mod_mad_minute_game = Blueprint("mad_minute_game", __name__, url_prefix="/games/mad_minute")

@mod_mad_minute_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 30 questions in order to play a game.

    Returns:
        JSON data for all of the questions.
    """

    questions = []

    numbers = {
        1: "一",
        2: "二",
        3: "三",
        4: "四",
        5: "五",
        6: "六",
        7: "七",
        8: "八",
        9: "九",
        10: "十"
    }

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

            answer = pinyin(numbers[first_number + second_number])
            prompt = pinyin(numbers[first_number]) + " + " + pinyin(numbers[second_number]) + " ="
        else:
            while first_number - second_number < 1:
                first_number = random.randint(1, 10)
                second_number = random.randint(1, 10)

            answer = pinyin(numbers[first_number - second_number])
            prompt = pinyin(numbers[first_number]) + " - " + pinyin(numbers[second_number]) + " ="

        question = {
            "prompt": prompt.lower(),
            "answer": answer.lower()
        }

        questions.append(question)

    return jsonify(questions)
