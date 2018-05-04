import boto3, json, os

from enum import Enum
from pynliner import Pynliner

class Email(Enum):
    VERIFY_EMAIL = 1
    FORGOT_PASSWORD = 2

def send(email, user):
    with open("./app/email/emails.json", "r") as f:
        data = json.loads(f.read())
        email_data = data[email.name.lower()]

    ses = boto3.client(
        "ses",
        aws_access_key_id=os.environ["SES_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SES_AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1"
    )

    settings = json.loads(user.settings)

    source = "%s <%s>" % ("Storytime", "no-reply@storytime.works")

    destination = {
        "ToAddresses": [
            "%s %s <%s>" % (settings["profile"]["first_name"], settings["profile"]["last_name"], "jack@storytime.works")
        ]
    }

    with open("./app/email/template.html", "r") as f:
        html = f.read()

    for key in email_data:
        html = html.replace("{%s}" % key, email_data[key])

    with open("./app/email/template.css", "r") as f:
        css = f.read()

    htmlData = Pynliner().from_string(html).with_cssString(css).run()

    message = {
        "Subject": {
            "Data": email_data["subject"]
        },
        "Body": {
            "Html": {
                "Data": htmlData
            },
            "Text": {
                "Data": email_data["body"]
            }
        }
    }

    ses.send_email(
        Source=source,
        Destination=destination,
        Message=message
    )
