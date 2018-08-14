from flask import Blueprint, jsonify, request, Response
from flask_login import current_user, login_required
import jieba, json, math, numpy as np

from app import admin_required, db
from app.chinese import pinyin, segment
from app.mod_games import Game
from app.mod_games.models import GameResult
import app.mod_games.mod_scribe.errors as errors
import app.mod_passages.errors as passage_errors
from app.mod_games.mod_scribe.models import ScribeQuestion, ScribeResult
from app.mod_mastery import update_masteries
from app.mod_passages.models import Passage
from app.mod_vocab.models import Entry
from app.utils import check_body

mod_scribe_game = Blueprint("scribe_game", __name__, url_prefix="/games/scribe")

@mod_scribe_game.route("/play", methods=["GET"])
@login_required
def play_game(words=None):
    """Retrieves about 10 questions in order to play Scribe.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return Scribe questions for this user
    questions = ScribeQuestion.play_game(words)
    return jsonify(questions)

@mod_scribe_game.route("/play/passages/<passage_id>", methods=["GET"])
@login_required
def play_game_for_passage(passage_id):
    """Plays Scribe according to the contents of a passage.

    Parameters:
        passage_id: The id of the passage to play this game with.

    Returns:
        JSON data of the game data.
    """

    # Retrieve the passage with the id passed to us
    passage = Passage.query.filter_by(id=passage_id).first()

    # Return 404 if the passage doesn't exist
    if passage is None:
        return passage_errors.passage_not_found()

    # Load the passage's new words list and use it to return game data
    words = json.loads(passage.new_words)
    return play_game(words)

@mod_scribe_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game and stores any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(request, ["correct", "correct_question_ids", "correct_words", "wrong", "wrong_question_ids", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_question_ids = request.json["correct_question_ids"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_question_ids = request.json["wrong_question_ids"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, Game.SCRIBE, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Scribe game result
    scribe_result = ScribeResult(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
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
            ScribeQuestion.english.like(query) |
            ScribeQuestion.other_english_answers.like(query)
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
        other_english_answers: Other acceptable answers for the English
            translation of this question.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["chinese", "english", "other_english_answers"]):
        return errors.missing_create_question_parameters()

    chinese = request.json["chinese"]
    english = request.json["english"]
    other_english_answers = request.json["other_english_answers"]

    # Create the question and store it in MySQL
    question = ScribeQuestion(chinese, english, other_english_answers)
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
        chinese: The Chinese prompt for this question.
        english: The english translation of the prompt.
        other_english_answers: Other acceptable answers for the English
            translation of this question.

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
        question.pinyin = pinyin(value)
        question.words = json.dumps(segment(value))
        question.words_pinyin = json.dumps([pinyin(word) for word in segment(value)])
    elif key == "english":
        question.english = value
    elif key == "other_english_answers":
        question.other_english_answers = json.dumps(value)

    # Save changes in MySQL
    db.session.commit()

    # Return updated question JSON data
    return jsonify(question.serialize())

@mod_scribe_game.route("/status", methods=["GET"])
@admin_required
def get_status():
    questions = ScribeQuestion.query.all()

    # A list of all of the words seen in every Scribe question
    words = set()

    for question in questions:
        # Get the words in each question's prompt with jieba
        question_words = [word for word in segment(question.chinese)]

        # Add this question's words to the words set
        words.update(question_words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return json.dumps(list(words), ensure_ascii=False)

@mod_scribe_game.route("/update", methods=["PUT"])
@admin_required
def update_scribe_questions():
    questions = ScribeQuestion.query.all()

    for question in questions:
        question.pinyin = pinyin(question.chinese)
        question.words = json.dumps(segment(question.chinese))
        question.words_pinyin = json.dumps([pinyin(word).lower() for word in segment(question.chinese)])

    db.session.commit()
    return "", 204
