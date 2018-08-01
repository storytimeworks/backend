from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_socketio import emit
from io import BytesIO
from scipy.io import wavfile
from threading import Thread
import json, numpy as np, os, requests, wave

from app import admin_required, db, socket
from app.mod_games.mod_speaker.models import SpeakerQuestion, SpeakerResult
from app.utils import check_body

mod_speaker_game = Blueprint("speaker_game", __name__, url_prefix="/games/speaker")

n_quiet = 0
speaking = False

stream = None
output = None

@socket.on("audio")
def audio(data):
    global n_quiet, speaking, stream, output

    print("audio")

    raw_data = BytesIO(data)

    rate, data = wavfile.read(raw_data)
    avg = np.abs(np.mean(data))

    if avg < 2:
        n_quiet += 1
    else:
        wav_data = wave.open(raw_data, "rb")

        if not speaking:
            print("Recording")

            stream = BytesIO()
            output = wave.open(stream, "wb")

            output.setparams(wav_data.getparams())

        output.writeframes(wav_data.readframes(wav_data.getnframes()))

        n_quiet = 0
        speaking = True

    if n_quiet == 5 and speaking:
        speaking = False

        print("Stopping")

        output.close()

        audio_data = stream.getvalue()

        def process_audio():
            with open("audio.wav", "wb") as f:
                f.write(audio_data)

            url = "https://speech.platform.bing.com/speech/recognition/dictation/cognitiveservices/v1" + \
                "?language=zh-CN" + \
                "&format=simple"

            headers = {
                "Content-Type": "audio/wav; codec=audio/pcm; samplerate=" + str(rate),
                "Ocp-Apim-Subscription-Key": os.environ["BING_SPEECH_API_KEY"]
            }

            r = requests.post(url, data=audio_data, headers=headers)
            r.encoding = "utf-8"

            print(r.text)
            # emit("results", json.loads(r.text))

        process_thread = Thread(target=process_audio)
        process_thread.start()

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
def check_answer():
    return "", 204

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
