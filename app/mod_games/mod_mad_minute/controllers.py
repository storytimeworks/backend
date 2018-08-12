from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

import random
from shushu import convert

from app import db
from app.chinese import pinyin
from app.mod_games import Game
from app.mod_games.models import GameResult
from app.mod_games.mod_mad_minute.models import MadMinuteResult
from app.mod_mastery import update_masteries
from app.utils import check_body

mod_mad_minute_game = Blueprint("mad_minute_game", __name__, url_prefix="/games/mad_minute")

@mod_mad_minute_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 40 questions in order to play a game.

    Returns:
        JSON data for all of the questions.
    """

    questions = []

    # Generate 30 questions for Mad Minute. This needs to be
    # updated later to support more difficult questions,
    # according to the user's experience
    for _ in range(40):
        first_number = 5
        second_number = 10

        answer = ""
        prompt = ""

        # True if this should be an addition question
        addition = random.randint(0, 1) == 0

        if addition:
            # Make sure that the summands and sum ≤ 10
            while first_number + second_number > 10:
                first_number = random.randint(1, 10)
                second_number = random.randint(1, 10)

            # Make the answer and prompt to return later
            answer = convert(first_number + second_number)
            prompt = pinyin(convert(first_number)) + " + " + pinyin(convert(second_number)) + " ="
        else:
            # Make sure that the all values ≤ 10
            while first_number - second_number < 1:
                first_number = random.randint(1, 10)
                second_number = random.randint(1, 10)

            # Make the answer and prompt to return later
            answer = convert(first_number - second_number)
            prompt = pinyin(convert(first_number)) + " - " + pinyin(convert(second_number)) + " ="

        prompt = prompt.lower()

        if len([x for x in questions if x["prompt"] == prompt]) > 0:
            # Make sure this question isn't a duplicate
            continue
        else:
            # Create the question data
            question = {
                "addition": addition,
                "answer": answer,
                "answer_pinyin": pinyin(answer).lower(),
                "first_number": first_number,
                "prompt": prompt.lower(),
                "second_number": second_number,
                "words": list(set([
                    convert(first_number),
                    convert(second_number),
                    answer
                ]))
            }

            # Add this question to the questions array
            questions.append(question)

    # Return questions array as JSON
    return jsonify(questions)

@mod_mad_minute_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game, storing any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(request, ["correct", "correct_words", "wrong", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, Game.MAD_MINUTE, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed mad minute game result
    mad_minute_result = MadMinuteResult(current_user.id, result.id, correct, wrong)
    db.session.add(mad_minute_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())
