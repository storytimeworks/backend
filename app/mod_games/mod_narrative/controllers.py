from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import admin_required, db
from app.mod_games.models import GameResult
from app.mod_games.mod_narrative.models import NarrativeQuestion, NarrativeResult
from app.mod_mastery import update_masteries
from app.mod_passages.models import Passage
import app.mod_passages.errors as passage_errors
from app.utils import check_body

mod_narrative_game = Blueprint("narrative_game", __name__, url_prefix="/games/narrative")

@mod_narrative_game.route("/play", methods=["GET"])
@login_required
def play_game(words=None):
    """Retrieves 3 questions in order to play Narrative.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return Narrative questions for this user
    questions = NarrativeQuestion.play_game(words)
    return jsonify(questions)

@mod_narrative_game.route("/play/passages/<passage_id>", methods=["GET"])
@login_required
def play_game_for_passage(passage_id):
    """Plays Narrative according to the contents of a passage.

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

@mod_narrative_game.route("/finish", methods=["POST"])
@login_required
def finish_game():
    """Completes a game and stores any necessary data.

    Returns:
        JSON data of the completed game.
    """

    # Ensure all necessary parameters are here
    if not check_body(reuqest, ["correct", "correct_question_ids", "correct_words", "wrong", "wrong_question_ids", "wrong_words"]):
        return errors.missing_finish_parameters()

    correct = request.json["correct"]
    correct_question_ids = request.json["correct_question_ids"]
    correct_words = request.json["correct_words"]
    wrong = request.json["wrong"]
    wrong_question_ids = request.json["wrong_question_ids"]
    wrong_words = request.json["wrong_words"]

    # Save generic game result
    result = GameResult(current_user.id, Game.NARRATIVE, 0)
    db.session.add(result)
    db.session.flush()

    # Save more detailed Narrative game result
    narrative_result = NarrativeResult(current_user.id, result.id, correct, wrong, correct_question_ids, wrong_question_ids)
    db.session.add(narrative_result)
    db.session.commit()

    # Update all masteries with words the user has practiced
    update_masteries(current_user.id, correct_words, wrong_words)

    # Return the general game result as JSON data
    return jsonify(result.serialize())

@mod_narrative_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all Narrative questions.

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
        questions = NarrativeQuestion.query.filter(
            NarrativeQuestion.prompt.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = NarrativeQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_narrative_game.route("/questions/<question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """Retrieves a Narrative question.

    Returns:
        JSON data of the question.
    """

    question = NarrativeQuestion.query.filter_by(id=question_id).first()

    if question is None:
        return errors.question_not_found()
    else:
        return jsonify(question.serialize())

@mod_narrative_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for Narrative.

    Body:
        prompts: The Chinese prompts that the user listens to.
        choices: The answer choices for each prompt.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompts", "choices"]):
        return errors.missing_create_question_parameters()

    prompts = request.json["prompts"]
    choices = request.json["choices"]

    # Create the question and store it in MySQL
    question = NarrativeQuestion(prompts, choices)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())

@mod_narrative_game.route("/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates a Narrative question. Currently only one key can be updated at a time.

    Body:
        prompts: The Chinese prompts that the user listens to.
        choices: The answer choices for each prompt.

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
    question = NarrativeQuestion.query.filter_by(id=question_id).first()

    # Return 404 if the question doesn't exist
    if question is None:
        return errors.question_not_found()

    # Update the question accordingly, depending on the key and value
    if key == "prompts":
        question.prompts = json.dumps(prompts)

        words = []

        for prompt in prompts:
            words.extend(segment(prompt))

        self.words = json.dumps(words)
    elif key == "choices":
        question.choices = json.dumps(choices)

    # Save changes in MySQL
    db.session.commit()

    # Return updated question JSON data
    return jsonify(question.serialize())
