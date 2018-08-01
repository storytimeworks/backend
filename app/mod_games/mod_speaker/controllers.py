from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_socketio import emit
from io import BytesIO
from scipy.io import wavfile
import numpy as np, os, requests

from app import admin_required, db, socket
from app.mod_games.mod_speaker.models import SpeakerQuestion, SpeakerResult
from app.utils import check_body

mod_speaker_game = Blueprint("speaker_game", __name__, url_prefix="/games/speaker")

n_quiet = 0
speaking = False

@socket.on("audio")
def audio(data):
    global n_quiet, speaking

    rate, data = wavfile.read(BytesIO(data))
    avg = np.mean(data)

    if np.abs(avg) < 5:
        n_quiet += 1
    else:
        if not speaking:
            emit("record_audio")

        n_quiet = 0
        speaking = True

    if n_quiet == 5:
        speaking = False

        emit("send_audio")

@mod_speaker_game.route("/play", methods=["GET"])
@login_required
def play_game(words=None):
    """Retrieves about 3 questions in order to play Speaker.

    Returns:
        JSON data for all of the questions.
    """

    # Retrieve and return Speaker questions for this user
    questions = SpeakerQuestion.play_game(words)
    return jsonify(questions)

@mod_speaker_game.route("/check", methods=["POST"])
@login_required
def check_answer(audio_data=None):
    if audio_data is None:
        audio_data = request.files["file"].read()

    url = "https://speech.platform.bing.com/speech/recognition/dictation/cognitiveservices/v1" + \
        "?language=zh-CN" + \
        "&format=simple"

    headers = {
        "Content-Type": "audio/wav; codec=audio/pcm; samplerate=16000",
        "Ocp-Apim-Subscription-Key": os.environ["BING_SPEECH_API_KEY"]
    }

    r = requests.post(url, data=audio_data, headers=headers)
    r.encoding = "utf-8"

    return r.text

@mod_speaker_game.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """Retrieves all Speaker questions.

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
        questions = SpeakerQuestion.query.filter(
            SpeakerQuestion.chinese.like(query)
        ).all()
    else:
        # Retrieve and return all questions
        questions = SpeakerQuestion.query.all()

    # Return questions JSON data
    questions_data = [question.serialize() for question in questions]
    return jsonify(questions_data)

@mod_speaker_game.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """Creates a question for Speaker.

    Body:
        prompt: The Chinese prompt for this question.

    Returns:
        JSON data of the question.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["prompt"]):
        return errors.missing_create_question_parameters()

    prompt = request.json["prompt"]

    # Create the question and store it in MySQL
    question = SpeakerQuestion(prompt)
    db.session.add(question)
    db.session.commit()

    # Return JSON data of the question
    return jsonify(question.serialize())
