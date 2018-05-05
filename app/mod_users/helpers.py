import re, validators
from zxcvbn import zxcvbn

import app.mod_users.errors as errors
from app.mod_users.models import User

def validate_username(username):
    if len(username) < 4:
        # Ensure the username is at least 4 characters long
        return errors.short_username()
    elif len(username) > 16:
        # Ensure the username is at most 16 characters long
        return errors.long_username()
    elif username[0] == "-" or username[0] == "_":
        # Ensure the username doesn't start with a dash or an underscore
        return errors.no_dash_start_username()
    elif re.match("^[\w-]+$", username) is None:
        # Ensure the username is alphanumeric + dashes and underscores
        return errors.invalid_username()
    elif User.query.filter_by(username=username).count() > 0:
        # Ensure the username isn't already taken
        return errors.username_taken()

def validate_email(email):
    if User.query.filter_by(email=email).count() > 0:
        # Ensure the email address hasn't already been used
        return errors.email_used()
    elif not validators.email(email):
        # Ensure the email address is valid
        return errors.invalid_email()

def validate_password(password, inputs):
    # zxcvbn throws an error if password is empty string, so catch this early
    if len(password) == 0:
        return errors.missing_registration_parameters()

    password_strength = zxcvbn(password, user_inputs=inputs)
    if password_strength["score"] < 2:
        return errors.weak_password(password_strength["feedback"])
