from flask import Blueprint, jsonify, request

import base64, boto3, os, uuid
from io import BytesIO
from PIL import Image

mod_writer_game = Blueprint("writer_game", __name__, url_prefix="/games/writer")

@mod_writer_game.route("/answer", methods=["POST"])
def answer_question():
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

    filename = "2/%s.png" % str(uuid.uuid4())
    s3.put_object(Body=data, Bucket="storytime-writer", Key=filename)

    return ("", 204)
