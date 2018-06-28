import boto3, json, os

from enum import Enum
from pynliner import Pynliner

class Email(Enum):
    VERIFY_EMAIL = 1
    FORGOT_PASSWORD = 2

def send(email, user, data):
    # Ensure that the email is valid
    if type(email) is not Email:
        raise Exception("email must be a valid Email type")

    email_address = user.email

    if email == Email.VERIFY_EMAIL and user.pending_email:
        email_address = user.pending_email

    # Don't send emails when not in production
    if os.environ["ENVIRONMENT"] == "development":
        print("Development environment, assume an email was sent to " + email_address)
        return

    # Read template data
    with open("./app/email/emails.json", "r") as f:
        emails = json.loads(f.read())
        email_data = emails[email.name.lower()]

    # Create the SES client
    ses = boto3.client(
        "ses",
        aws_access_key_id=os.environ["SES_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SES_AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1"
    )

    # Set the name and email address of the sender
    source = "%s <%s>" % ("Storytime", "no-reply@storytime.works")

    # Load user settings to see if the user's first and last names have been
    # saved. Otherwise, use their username for the email.
    settings = json.loads(user.settings)
    username = user.username
    first_name = settings["profile"]["first_name"]
    last_name = settings["profile"]["last_name"]

    if len(first_name) > 0 and len(last_name) > 0:
        recipient = "%s %s" % (first_name, last_name)
    else:
        recipient = username

    # Set the recipient name and email address
    destination = {
        "ToAddresses": [
            "%s <%s>" % (recipient, email_address)
        ]
    }

    # Read the template HTML
    with open("./app/email/template.html", "r") as f:
        html = f.read()

    # Replace template variable names with correct values
    for key in email_data:
        html = html.replace("{%s}" % key, email_data[key])

    # Set the link in the email depending on which type of email this is
    if email == Email.VERIFY_EMAIL:
        html = html.replace("{link}", "https://storytime.works/verify-email?code=%s" % data.code)
    elif email == Email.FORGOT_PASSWORD:
        html = html.replace("{link}", "https://storytime.works/reset-password?code=%s" % data.code)

    # Read the template CSS
    with open("./app/email/template.css", "r") as f:
        css = f.read()

    # Combine the HTML and CSS so it can be used in an email
    htmlData = Pynliner().from_string(html).with_cssString(css).run()

    # Set the email subject, text, and HTML for email clients that support it
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

    # Send the email
    ses.send_email(
        Source=source,
        Destination=destination,
        Message=message
    )
