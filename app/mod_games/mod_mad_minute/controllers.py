from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

import random
from shushu import convert

from app import db
from app.mod_games.models import GameResult
from app.mod_games.mod_mad_minute import check_body
from app.mod_games.mod_mad_minute.models import MadMinuteResult
from app.mod_mastery.models import Mastery
from app.mod_vocab.models import Entry
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
            "answer_pinyin": pinyin(answer).lower(),
            "words": list(set([
                convert(first_number),
                convert(second_number),
                answer
            ]))
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

    if not check_body(request, ["correct", "correct_words", "wrong", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_words = request.json["wrong_words"]

    result = GameResult(current_user.id, 1, 0)
    db.session.add(result)
    db.session.flush()

    mad_minute_result = MadMinuteResult(current_user.id, result.id, correct, wrong)
    db.session.add(mad_minute_result)
    db.session.commit()

    words = {}

    for word in correct_words:
        if word in words:
            words[word] += 1
        else:
            words[word] = 1

    for word in wrong_words:
        if word in words:
            words[word] -= 1
        else:
            words[word] = -1

    chinese_words = [word for word in words]
    entries = Entry.query.filter(Entry.chinese.in_(chinese_words)).all()
    entry_ids = []

    for entry in entries:
        entry_ids.append(entry.id)

        words[entry.id] = words[entry.chinese]
        del words[entry.chinese]

    masteries = Mastery.query.filter_by(user_id=current_user.id).filter(Mastery.entry_id.in_(entry_ids))

    for mastery in masteries:
        mastery.mastery += words[mastery.entry_id]
        del words[mastery.entry_id]

        if mastery.mastery < 0:
            mastery.mastery = 0
        elif mastery.mastery > 10:
            mastery.mastery = 10

    new_masteries = []

    for word in words:
        mastery = Mastery(current_user.id, word, max(0, words[word]))
        new_masteries.append(mastery)

    db.session.add_all(new_masteries)
    db.session.commit()

    return jsonify(result.serialize())
