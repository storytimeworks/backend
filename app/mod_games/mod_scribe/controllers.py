from flask import Blueprint, jsonify, request, Response
from flask_login import current_user, login_required
import jieba, json, math, numpy as np

from app import admin_required, db
from app.mod_games.models import GameResult
import app.mod_games.mod_scribe.errors as errors
import app.mod_passages.errors as passage_errors
from app.mod_games.mod_scribe.models import ScribeQuestion, ScribeResult
from app.mod_mastery import update_masteries
from app.mod_mastery.models import Mastery
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

    # The number of questions to return
    NUM_QUESTIONS = 10

    # The greatest number of questions to show the user that they have
    # previously answered incorrectly
    MAX_WRONG_QUESTIONS = 3

    # The greatest number of questions to show the user that they have
    # previously answered correctly
    MAX_CORRECT_QUESTIONS = 2

    # If the user has answered fewer than MAX_WRONG_QUESTIONS questions
    # incorrectly, this value may be used in place of MAX_CORRECT_QUESTIONS
    MAX_CORRECT_QUESTIONS_WITH_FEW_WRONG_QUESTIONS = 3

    # Mean of the normal distribution used to find question difficulties
    DIFFICULTY_RNORM_MEAN = 17.5

    # Standard deviation of the normal distribution used to find question
    # difficulties
    DIFFICULTY_RNORM_STDEV = 5

    # The list of ids of the questions that should be included in the final result
    question_ids_to_show = []

    # Order by timestamp ascending in order to calculate streaks correctly
    results = ScribeResult.query.filter_by(user_id=current_user.id) \
                .order_by(ScribeResult.timestamp.asc()).all()

    # Set of the question ids that the user has already seen
    seen_question_ids = set()

    # Maps question ids to the number of games ago where they were last seen
    question_games_ago = {}

    # Maps question ids to the number of times they've been answered correctly
    # in a row. If last answered incorrectly, this equals -1. If never seen
    # before, the question id will not be in this dictionary
    question_streaks = {}

    # Loop through past Scribe results
    for (idx, result) in enumerate(results):
        # Loop through questions answered correctly to calculate streaks
        for id in json.loads(result.correct_question_ids):
            if id in question_streaks:
                question_streaks[id] += 1
            else:
                question_streaks[id] = 1

            # Games ago = number of games played - current index in loop
            question_games_ago[id] = len(results) - idx

            # Add this id to the seen_question_ids set
            seen_question_ids.add(id)

        # Loop through questions answered incorrectly to reset streaks
        for id in json.loads(result.wrong_question_ids):
            question_streaks[id] = -1

            # Games ago = number of games played - current index in loop
            question_games_ago[id] = len(results) - idx

            # Add this id to the seen_question_ids set
            seen_question_ids.add(id)

    # Get all of the questions that were last answered incorrectly
    wrong_questions = [x for x in question_streaks if question_streaks[x] == -1]

    if len(wrong_questions) > 0:
        # Make sure our sample size is not greater than the list's length
        num_wrong_questions_to_show = min(len(wrong_questions), MAX_WRONG_QUESTIONS)

        # Randomly sample the wrong_questions list
        wrong_questions_to_show = np.random.choice(wrong_questions, num_wrong_questions_to_show, False)

        # Add these question ids to the result list
        question_ids_to_show.extend(wrong_questions_to_show)

    # Get all of the questions that were last answered correctly, but make sure
    # they weren't answered too recently. games_ago must be >= (streak)^2
    correct_questions = [x for x in question_streaks if question_streaks[x] >= 0 and question_games_ago[x] >= question_streaks[x] ** 2]

    if len(correct_questions) > 0:
        # Make sure our sample size is not greater than the list's length
        num_correct_questions_to_show = min(len(correct_questions), MAX_CORRECT_QUESTIONS if len(wrong_questions) < MAX_WRONG_QUESTIONS else MAX_CORRECT_QUESTIONS_WITH_FEW_WRONG_QUESTIONS)

        # Randomly sample the correct questions list
        correct_questions_to_show = np.random.choice(correct_questions, num_correct_questions_to_show, False)

        # Add these question ids to the result list
        question_ids_to_show.extend(correct_questions_to_show)

    # Make sure questions that have been seen before but were not selected are
    # not in the pool of questions that may be picked at random. Include
    # questions that will be shown to the user so we can get their data
    excluded_question_ids = list(seen_question_ids)
    excluded_question_ids = [id for id in excluded_question_ids if id not in question_ids_to_show]

    questions = []

    if words == None or len(words) == 0:
        # Retrieve all Scribe questions that have not been seen before by the user
        questions = ScribeQuestion.query.filter(ScribeQuestion.id.notin_(excluded_question_ids)).all()
    else:
        # Create a filter that checks for the words provided
        word_filter = ScribeQuestion.chinese.contains(words[0])

        for word in words[1:]:
            word_filter = word_filter | ScribeQuestion.chinese.contains(word)

        # Retrieve all Scribe questions that match both filters
        questions = ScribeQuestion.query.filter(
            ScribeQuestion.id.notin_(excluded_question_ids) & word_filter
        ).all()

    questions_data = [question.serialize() for question in questions]

    # After getting data of questions to show, remove them from questions_data
    # so they will not be randomly picked again later
    questions_to_show = [datum for datum in questions_data if datum["id"] in question_ids_to_show]
    questions_data = [datum for datum in questions_data if datum["id"] not in question_ids_to_show]

    # A list of all of the words seen in every Scribe question
    words = set()

    for question in questions_data:
        # Get the words in each question's prompt with jieba
        question_words = [word for word in jieba.cut(question["chinese"], cut_all=False)]
        question["words"] = question_words

        # Add this question's words to the words set
        words.update(question_words)

    # Only retrieve the entries that we need
    entries = Entry.query.filter(Entry.chinese.in_(words)).all()
    entry_ids = [entry.id for entry in entries]

    # Only retrieve the masteries that we need
    masteries = Mastery.query.filter(
        (Mastery.user_id == current_user.id) &
        Mastery.entry_id.in_(entry_ids)
    ).all()

    # Maps Chinese words to their difficulty scores
    difficulties = {}

    # Calculate the difficulty score of each word, using the lists of entries
    # and the user's masteries with them
    for entry in entries:
        mastery = next((x for x in masteries if x.entry_id == entry.id), None)

        if mastery is None:
            # An entry exists for this word, but the user has never encountered
            # it before
            difficulties[entry.chinese] = {
                "new": True,
                "score": 10
            }
        else:
            difficulties[entry.chinese] = {
                "new": False,
                "score": 10 - mastery.mastery
            }

    word_data = {entry.chinese: {
        "chinese": entry.chinese,
        "english": entry.english,
        "pinyin": entry.pinyin
    } for entry in entries}

    # Calculate the difficulty score of each question, using the word difficulty
    # scores from above
    for question in questions_data:
        difficulty = 0
        new_words = []

        for word in question["words"]:
            if word in difficulties:
                difficulty += difficulties[word]["score"]

                if difficulties[word]["new"]:
                    new_words.append(word)
            else:
                # An entry doesn't exist for this word, we don't know if the
                # user has encountered it before or not
                difficulty += 10

        question["difficulty"] = difficulty

        # Get new word data from word_data above and add to the dictionary
        new_words = list(set(new_words))
        question["new_words"] = list(map(lambda x: word_data[x], new_words))

    # Sort questions_data by difficulty scores so we can use binary search
    questions_data.sort(key=lambda x: x["difficulty"])

    # Count how many questions we need to find at random
    num_other_questions = NUM_QUESTIONS - len(question_ids_to_show)

    # Use the normal distribution to calculate the targeted difficulty levels of
    # questions we want to find at random
    difficulties = [math.floor(x) for x in np.random.normal(DIFFICULTY_RNORM_MEAN, DIFFICULTY_RNORM_STDEV, num_other_questions)]

    # Use binary search to find questions that have difficulty scores that match
    # or are closest to the target difficulty scores in the difficulties array
    for difficulty in difficulties:
        first = 0
        last = len(questions_data) - 1
        found = False

        while first <= last and not found:
            midpoint = (first + last) // 2

            if questions_data[midpoint]["difficulty"] == difficulty:
                questions_to_show.append(questions_data[midpoint])
                found = True

                # Delete from questions_data so this question is not randomly
                # picked again later
                del questions_data[midpoint]
            else:
                if difficulty < questions_data[midpoint]["difficulty"]:
                    last = midpoint - 1
                else:
                    first = midpoint + 1

        if not found:
            questions_to_show.append(questions_data[first])

            # Delete from questions_data so this question is not randomly picked
            # again later
            del questions_data[first]

    np.random.shuffle(questions_to_show)

    # Return JSON data
    return jsonify(questions_to_show)

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
    result = GameResult(current_user.id, 2, 0)
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
        question_words = [word for word in jieba.cut(question.chinese, cut_all=False)]

        # Add this question's words to the words set
        words.update(question_words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return json.dumps(list(words), ensure_ascii=False)
