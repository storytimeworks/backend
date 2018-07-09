from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import jieba, json, math, numpy as np

from app import admin_required, db
from app.mod_games.models import GameResult
import app.mod_games.mod_scribe.errors as errors
from app.mod_games.mod_scribe.models import ScribeQuestion, ScribeResult
from app.mod_mastery import update_masteries
from app.mod_mastery.models import Mastery
from app.mod_vocab.models import Entry
from app.utils import check_body

mod_scribe_game = Blueprint("scribe_game", __name__, url_prefix="/games/scribe")

@mod_scribe_game.route("/play", methods=["GET"])
@login_required
def play_game():
    """Retrieves about 10 questions in order to play Scribe.

    Returns:
        JSON data for all of the questions.
    """

    question_ids_to_show = []

    results = ScribeResult.query.filter_by(user_id=current_user.id).order_by(ScribeResult.timestamp.asc()).all()

    question_games_ago = {}
    question_streaks = {}

    for (idx, result) in enumerate(results):
        for id in json.loads(result.correct_question_ids):
            if id in question_streaks:
                question_streaks[id] += 1
            else:
                question_streaks[id] = 1

            question_games_ago[id] = len(results) - idx

        for id in json.loads(result.wrong_question_ids):
            question_streaks[id] = -1

            question_games_ago[id] = len(results) - idx

    previously_wrong_questions = [x for x in question_streaks if question_streaks[x] == -1]

    if len(previously_wrong_questions) > 0:
        previously_wrong_questions_to_show = np.random.choice(previously_wrong_questions, min(len(previously_wrong_questions), 3), False)
        question_ids_to_show.extend(previously_wrong_questions_to_show)

    previously_correct_questions = [x for x in question_streaks if question_streaks[x] >= 0 and question_games_ago[x] >= question_streaks[x] ** 2]

    if len(previously_correct_questions) > 0:
        num_previously_correct_questions_to_show = 3 if len(previously_wrong_questions) < 3 else 2

        previously_correct_questions_to_show = np.random.choice(previously_correct_questions, min(len(previously_correct_questions), num_previously_correct_questions_to_show), False)
        question_ids_to_show.extend(previously_correct_questions_to_show)

    questions = ScribeQuestion.query.all()
    questions_data = [question.serialize() for question in questions]

    words = set()

    for question in questions_data:
        question_words = [word for word in jieba.cut(question["chinese"], cut_all=False)]
        words.update(question_words)

        question["words"] = question_words

    entries = Entry.query.filter(Entry.chinese.in_(words))
    entry_ids = [entry.id for entry in entries]

    masteries = Mastery.query.filter(
        (Mastery.user_id == current_user.id) &
        Mastery.entry_id.in_(entry_ids)
    ).all()

    difficulties = {}

    for entry in entries:
        mastery = next((x for x in masteries if x.entry_id == entry.id), None)

        if mastery is None:
            difficulties[entry.chinese] = 10
        else:
            difficulties[entry.chinese] = 10 - mastery.mastery

    for question in questions_data:
        difficulty = 0

        for word in question["words"]:
            if word in difficulties:
                difficulty += difficulties[word]
            else:
                difficulty += 10

        question["difficulty"] = difficulty

    questions_to_show = []

    questions_to_show.extend([data for data in questions_data if data["id"] in question_ids_to_show])
    questions_data = [data for data in questions_data if data["id"] not in question_ids_to_show]

    questions_data.sort(key=lambda x: x["difficulty"])

    num_other_questions = 10 - len(question_ids_to_show)
    other_questions = []

    difficulties = [math.floor(x) for x in np.random.normal(17.5, 5, num_other_questions) if x <= 40]

    for difficulty in difficulties:
        first = 0
        last = len(questions_data) - 1
        found = False

        while first <= last and not found:
            midpoint = (first + last) // 2

            if questions_data[midpoint]["difficulty"] == difficulty:
                found = True
                questions_to_show.append(questions_data[midpoint])
            else:
                if difficulty < questions_data[midpoint]["difficulty"]:
                    last = midpoint - 1
                else:
                    first = midpoint + 1

        if not found:
            questions_to_show.append(questions_data[first])
            del questions_data[first]

    np.random.shuffle(questions_to_show)

    # Return JSON data
    return jsonify(questions_to_show)

@mod_scribe_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game and stores any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(request, ["correct", "correct_words", "question_ids", "wrong", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_words = request.json["correct_words"]
    question_ids = request.json["question_ids"]
    wrong = request.json["wrong"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, 2, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Scribe game result
    scribe_result = ScribeResult(current_user.id, result.id, correct, wrong, question_ids)
    db.session.add(scribe_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())

@mod_scribe_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all Scribe questions.

    Parameters:
        q: The query that should be used for the search.

    Returns:
        JSON data for all the questions.
    """

    questions = []

    if "q" in request.args:
        # Use the query to search for a question if one is included
        query = "%" + request.args.get("q") + "%"

        # Ensure the correct questions are being returned
        questions = ScribeQuestion.query.filter(
            ScribeQuestion.chinese.like(query) |
            ScribeQuestion.english.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = ScribeQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_scribe_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a Scribe question.

    Returns:
        JSON data of the question.
    """

    question = ScribeQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_scribe_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for Scribe.

    Body:
        chinese: The Chinese prompt for this question.
        english: The english translation of the prompt.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["chinese", "english"]):
        return errors.missing_create_question_parameters()

    chinese = request.json["chinese"]
    english = request.json["english"]

    # Create the question and store it in MySQL
    question = ScribeQuestion(chinese, english)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_scribe_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a Scribe question. Currently only one key can be updated at a
    time.

    Body:
        prompt: The prompt for this question.

    Returns:
        JSON data of the question.
    """

    key = None
    value = None

    # Try to get the key and value being updated for this question
    if request.json and len(request.json.keys()) > 0:
        key = list(request.json.keys())[0]
        value = request.json[key]
    else:
        return errors.missing_update_question_parameters()

    # Find the question being updated
    question = ScribeQuestion.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "chinese":
        question.chinese = value
    elif key == "english":
        question.english = value

    # Save changes in MySQL
    db.session.commit()

    # Return updated question JSON data
    return jsonify(question.serialize())
