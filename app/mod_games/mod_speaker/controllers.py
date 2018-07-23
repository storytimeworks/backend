from flask import Blueprint, jsonify, request
from flask_login import login_required
import os, requests

mod_speaker_game = Blueprint("speaker_game", __name__, url_prefix="/games/speaker")

@mod_speaker_game.route("/check", methods=["POST"])
@login_required
def check_answer():
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
