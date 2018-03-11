from flask import Blueprint, request, send_file
from io import BytesIO
import random
import requests

mod_speech = Blueprint("speech", __name__, url_prefix="/speech")

@mod_speech.route("/chinese", methods=["GET"])
def synthesize_chinese():
    text = request.args.get("text")

    # 0 = female, 1 = male
    voice = str(random.randint(0, 1))

    url = "http://tsn.baidu.com/text2audio" + \
        "?lan=zh" + \
        "&ctp=1" + \
        "&cuid=backend" + \
        "&tok=24.e052ae1a8291d52184779359fecc7a40.2592000.1523387524.282335-10910985" + \
        "&tex=" + text + \
        "&vol=9" + \
        "&per=" + voice + \
        "&spd=3" + \
        "&pit=5"

    r = requests.get(url)

    return send_file(
        BytesIO(r.content),
        attachment_filename="speech.mp3",
        mimetype="audio/mpeg"
    )
