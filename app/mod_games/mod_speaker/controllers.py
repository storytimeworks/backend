from flask import Blueprint, jsonify, request
from flask_login import login_required
import boto3, json, numpy as np, os, requests, uuid

from app import admin_required, db
from app.mod_games.mod_speaker.models import SpeakerQuestion, SpeakerResult
from app.utils import check_body

mod_speaker_game = Blueprint("speaker_game", __name__, url_prefix="/games/speaker")

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
    # Retrieve audio and answer data from the request
    answer = request.args.get("answer")
    audio_data = request.files["file"].read()

    # Send this audio to Bing's Speech Recognition API
    url = "https://speech.platform.bing.com/speech/recognition/dictation/cognitiveservices/v1" + \
        "?language=zh-CN" + \
        "&format=detailed"

    headers = {
        "Content-Type": "audio/wav; codec=audio/pcm; samplerate=16000",
        "Ocp-Apim-Subscription-Key": os.environ["BING_SPEECH_API_KEY"]
    }

    r = requests.post(url, data=audio_data, headers=headers)
    r.encoding = "utf-8"

    # Parse the results of the request
    correct = False
    data = r.json()
    status = data["RecognitionStatus"]

    if status == "Success":
        # Loop through results and see if any have high enough confidence
        for result in data["NBest"]:
            if result["Lexical"] == answer:
                correct = True

        # Upload the audio to S3 for training later
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
        )

        filename = str(uuid.uuid4())
        path = "speaker/%s/wrong/%s.wav" % (answer, filename)

        if correct:
            path = "speaker/%s/%s.wav" % (answer, filename)

        s3.put_object(Body=audio_data, Bucket="storytimeai", Key=path)

    # Create a result JSON object to send back to the browser
    result = {
        "correct": correct,
        "status": status
    }

    return jsonify(result)
