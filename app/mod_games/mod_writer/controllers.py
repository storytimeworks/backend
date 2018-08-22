from flask import Blueprint, jsonify, request, send_file

import base64, boto3, os, uuid
from io import BytesIO
from PIL import Image

from app import db
from app.utils import check_body
import app.mod_games.mod_writer.errors as errors
from app.mod_games.mod_writer.model import load_session, make_prediction
from app.mod_games.mod_writer import WriterAnswer

mod_writer_game = Blueprint("writer_game", __name__, url_prefix="/games/writer")
session = load_session()

@mod_writer_game.route("/answers", methods=["POST"])
def answer_question():
    """Scores a user's answer to a question and saves their answer for review.

    Body:
        image: A base64 representation of the image drawn by the user.

    Returns:
        JSON object with the resulting prediction.
    """

    # Ensure necessary parameters are here
    if not check_body(["image"]):
        return errors.missing_answer_parameters()

    # Resize the image for classification and convert to bytes
    base64_image = request.json["image"][22:]
    image = Image.open(BytesIO(base64.b64decode(base64_image)))
    image = image.resize((28, 28), Image.ANTIALIAS)

    data = BytesIO()
    image.save(data, format="PNG")
    data = data.getvalue()

    # Create client and save the image to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    filename = str(uuid.uuid4())
    path = "writer/unclassified/%s.png" % filename
    s3.put_object(Body=data, Bucket="storytimeai", Key=path)

    # Save path in S3 to MySQL
    answer = WriterAnswer(filename)
    db.session.add(answer)
    db.session.commit()

    # Predict the number depicted in the image and return the prediction
    prediction = make_prediction(session, image)
    return jsonify(prediction=prediction)

@mod_writer_game.route("/answers", methods=["GET"])
def get_answers():
    """Returns JSON data of all of the answers that haven't been scored yet.

    Returns:
        JSON array with unscored image paths.
    """

    # Retrieve answers from MySQL and return them
    answers = WriterAnswer.query.all()
    answers_data = [answer.serialize() for answer in answers]
    return jsonify(answers_data)

@mod_writer_game.route("/answers/<answer_id>", methods=["DELETE"])
def train_model(answer_id):
    """Deletes an answer from MySQL and uses it to train the model.

    Body:
        classification: The classification for this answer.

    Returns:
        204 no content.
    """

    # Ensure necessary parameters are here
    if not check_body(["classification"]):
        return errors.missing_train_parameters()

    classification = request.json["classification"]

    if classification < 0 or classification > 10:
        return errors.invalid_classification()

    # Create client and get the new and old filepaths
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    answer = WriterAnswer.query.filter_by(id=answer_id).first()
    new_path = "writer/%d/%s.png" % (classification, answer.name)
    old_path = "writer/unclassified/%s.png" % answer.name

    # If the classification = 0, the image is just being deleted. Otherwise, it
    # should be moved to its new location
    if classification > 0:
        s3.copy({
            "Bucket": "storytimeai",
            "Key": old_path
        }, "storytimeai", new_path)

    # Delete the image from S3
    s3.delete_object(Bucket="storytimeai", Key=old_path)

    # Delete answer from MySQL
    WriterAnswer.query.filter_by(id=answer_id).delete()

    return ("", 204)

@mod_writer_game.route("/answers/<answer_id>/image", methods=["GET"])
def get_answer_image(answer_id):
    """Retrieves an image from S3 for a specified answer.

    Returns:
        The answer's image.
    """

    # Get the answer from MySQL
    answer = WriterAnswer.query.filter_by(id=answer_id).first()

    # Create the S3 client and retrieve the image
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    image_data = s3.get_object(Bucket="storytimeai", Key="writer/unclassified/%s.png" % answer.name)["Body"].read()

    # Send the file back to the requester
    return send_file(
        BytesIO(image_data),
        attachment_filename="image.png",
        mimetype="image/png"
    )

@mod_writer_game.route("/train", methods=["POST"])
def train_model_directly():
    """Trains a model directly, without going through the game.

    Body:
        classification: The classification for this image.
        image: A base64 representation of the image drawn by the user.

    Returns:
        204 no content.
    """

    # Ensure necessary parameters are here
    if not check_body(["classification", "image"]):
        return errors.missing_train_parameters()

    classification = request.json["classification"]
    image = request.json["image"]

    # Process image so it can be stored for training
    base64_image = image[22:]
    img = Image.open(BytesIO(base64.b64decode(base64_image)))
    img = img.resize((28, 28), Image.ANTIALIAS)

    data = BytesIO()
    img.save(data, format="PNG")
    data = data.getvalue()

    # Create S3 client and save the image
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    filename = str(uuid.uuid4())
    path = "writer/%d/%s.png" % (classification, filename)
    s3.put_object(Body=data, Bucket="storytimeai", Key=path)

    # Return nothing, the action is done
    return ("", 204)
