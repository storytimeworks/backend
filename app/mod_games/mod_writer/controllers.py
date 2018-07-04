from flask import Blueprint, jsonify, request

import base64, boto3, os, uuid
from io import BytesIO
from PIL import Image

from app.mod_games.mod_writer.model import load_session, make_prediction

mod_writer_game = Blueprint("writer_game", __name__, url_prefix="/games/writer")
session = load_session()

@mod_writer_game.route("/answer", methods=["POST"])
def answer_question():
    character = request.json["character"]
    base64_image = request.json["image"][22:]
    image = Image.open(BytesIO(base64.b64decode(base64_image)))
    image = image.resize((28, 28), Image.ANTIALIAS)

    data = BytesIO()
    image.save(data, format="PNG")
    data = data.getvalue()

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    filename = str(character) + "/%s.png" % str(uuid.uuid4())
    s3.put_object(Body=data, Bucket="storytime-writer", Key=filename)

    return ("", 204)

@mod_writer_game.route("/test", methods=["POST"])
def test_answer():
    base64_image = request.json["image"][22:]

    image = Image.open(BytesIO(base64.b64decode(base64_image)))
    image = image.resize((28, 28), Image.ANTIALIAS)

    prediction = make_prediction(session, image)

    return jsonify({
        "prediction": int(prediction)
    })
