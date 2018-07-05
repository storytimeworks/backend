from flask import Blueprint, request, send_file
from flask_login import current_user

import boto3, json, os, random, requests, uuid
from io import BytesIO

from app import db
import app.mod_speech.errors as errors
from app.mod_speech.models import ChineseSpeechSynthesis, EnglishSpeechSynthesis
from app.mod_users.models import User

# Variable used to store the Baidu access token. Is replaced with the actual
# access token when the first speech request is made
baidu_access_token = "replace me"

mod_speech = Blueprint("speech", __name__, url_prefix="/speech")

@mod_speech.route("/chinese", methods=["GET"])
def synthesize_chinese():
    """Returns synthesized Chinese speech, in some audio format.

    Parameters:
        text: The text that needs to be synthesized.

    Returns:
        The audio file/stream that was generated with the given text.
    """

    # Save Baidu access token outside of this method
    global baidu_access_token

    if "text" not in request.args:
        return errors.text_not_provided()

    text = request.args.get("text")

    recording = None

    if "voice" in request.args:
        voice = int(request.args.get("voice"))
        recording = ChineseSpeechSynthesis.query.filter_by(source=text, voice=voice).first()
    else:
        recording = ChineseSpeechSynthesis.query.filter_by(source=text).first()

    # voice is defined out here so it can be sent to the database later
    voice = 0
    url = ""

    # Create the S3 client since it is needed no matter what
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    )

    if recording is not None:
        # Retrieve audio data from S3
        audio_data = s3.get_object(Bucket="storytimeai", Key="speech/%s" % recording.filename)["Body"].read()

        # Send the file back to the requester
        return send_file(
            BytesIO(audio_data),
            attachment_filename="speech.mp3",
            mimetype="audio/mpeg"
        )
    else:
        # Don't save new recordings in development environment
        if os.environ["ENVIRONMENT"] != "production":
            return errors.not_generating_speech()

        # If the recording hasn't been saved, check if the user is authenticated
        # If they are authenticated, save a new transcription from Baidu
        if current_user.is_active and current_user.is_admin:
            pass
        else:
            # No session exists, requester is not authenticated
            return errors.speech_not_found()

        # 0 = female, 1 = male
        voice = 0

        if "voice" in request.args:
            voice = int(request.args.get("voice"))
        else:
            voice = random.randint(0, 1)

        url = "http://tsn.baidu.com/text2audio" + \
            "?lan=zh" + \
            "&ctp=1" + \
            "&cuid=backend" + \
            "&tok=" + baidu_access_token + \
            "&tex=" + text + \
            "&vol=9" + \
            "&per=" + str(voice) + \
            "&spd=3" + \
            "&pit=5"

        # Download the audio file, from S3 or from Baidu
        r = requests.get(url)

        # Valid Baidu errors that we want to respond to
        baidu_errors = ["Access token invalid or no longer valid", "Access token expired"]

        if r.headers.get("Content-Type") == "application/json" and r.json()["err_detail"] in baidu_errors:
            # Request a new access token from Baidu if the one we have has expired
            # or if we haven't requested one yet
            token_url = "https://openapi.baidu.com/oauth/2.0/token" + \
                "?grant_type=client_credentials" + \
                "&client_id=" + os.environ["BAIDU_CLIENT_ID"] + \
                "&client_secret=" + os.environ["BAIDU_CLIENT_SECRET"]

            token_request = requests.get(token_url)

            # Retrieve the new access token and put it in the request URL
            new_access_token = token_request.json()["access_token"]
            url = url.replace(baidu_access_token, new_access_token)

            # Store the new access token
            baidu_access_token = new_access_token

            # Perform the request again, with the new access token
            r = requests.get(url)

        # At this point, we should have an audio file. If not, don't expose
        # anything we don't have to
        if r.headers.get("Content-Type") != "audio/mp3":
            return errors.issue_generating_speech()

        # Save this recording in S3 if it isn't already there
        filename = "%s.mp3" % str(uuid.uuid4())
        s3.put_object(Body=BytesIO(r.content), Bucket="storytimeai", Key="speech/%s" % filename)

        # Add new audio file to speech database
        synthesis = ChineseSpeechSynthesis(text, filename, voice)
        db.session.add(synthesis)
        db.session.commit()

        # Serve file to the user
        return send_file(
            BytesIO(r.content),
            attachment_filename="speech.mp3",
            mimetype="audio/mpeg"
        )

@mod_speech.route("/english", methods=["GET"])
def synthesize_english():
    text = request.args.get("text")

    recording = EnglishSpeechSynthesis.query.filter_by(source=text).first()

    audio_data = None

    # voice is defined out here so it can be sent to the database later
    voice = 0

    if recording:
        # If the recording has already been saved, load it from S3
        url = "https://s3.amazonaws.com/storytime-speech/" + recording.filename

        # Download the audio file from S3
        audio_data = requests.get(url).content
    else:
        # Don't save new recordings in development environment
        if os.environ["ENVIRONMENT"] != "production":
            return errors.not_generating_speech()

        # If the recording hasn't been saved, check if the user is authenticated
        # If they are authenticated, save a new transcription from AWS Polly
        if current_user.is_active and current_user.is_admin:
            pass
        else:
            # No session exists, requester is not authenticated
            return errors.speech_not_found()

        polly = boto3.client(
            "polly",
            aws_access_key_id=os.environ["POLLY_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["POLLY_AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-1"
        )

        # 0 = female, 1 = male
        voice = random.randint(0, 1)
        voice_id = "Joanna" if voice == 0 else "Matthew"

        response = polly.synthesize_speech(
            OutputFormat="mp3",
            Text=text,
            VoiceId=voice_id
        )

        # Save audio data from response from AWS Polly
        audio_data = response["AudioStream"].read()

    if not recording:
        # Save this recording in S3 if it isn't already there
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ["S3_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
        )

        filename = "%s.mp3" % str(uuid.uuid4())
        s3.put_object(Body=BytesIO(audio_data), Bucket="storytime-speech", Key=filename)

        # Add new audio file to speech database
        synthesis = EnglishSpeechSynthesis(text, filename, voice)
        db.session.add(synthesis)
        db.session.commit()

    # Serve file to the user
    return send_file(
        BytesIO(audio_data),
        attachment_filename="speech.mp3",
        mimetype="audio/mpeg"
    )
