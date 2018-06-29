import bcrypt, boto3, json, os
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

# Storytime imports
from app import admin_required, db, log_error
from app.email import Email, send
from app.mod_users import validate_username, validate_email, validate_password
import app.mod_users.errors as errors
from app.mod_users.models import User, EmailVerification, Invitation, PasswordReset
from app.utils import check_body

# Create users Flask blueprint
mod_users = Blueprint("users", __name__, url_prefix="/users")

@mod_users.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieves data for a user. Some data is omitted or included depending on
    the permissions of the person requesting the data.

    Args:
        user_id: The id of the user whose data is being requested.

    Returns:
        The JSON data for this user.
    """

    # Find user in the SQL database
    user = User.query.filter_by(id=user_id).first()

    # Return 404 if there is no user with this id
    if user is None:
        return errors.user_not_found()

    # full = Should the user's full data be returned. False if sensitive data
    # should be omitted.
    full = False

    # Check if anyone is currently authenticated
    if current_user.is_active:
        # Sensitive data should be returned if the user is requesting his/her
        # own data or if the requester is an admin
        if current_user.id == int(user_id) or current_user.is_admin:
            full = True

    # Return the user's JSON data
    return jsonify(user.serialize(full))

@mod_users.route("", methods=["POST"])
def register():
    """Creates a new user who can log in and use Storytime.

    Body:
        username: The username for the new user.
        email: The new user's email address.
        password: The new user's password.

    Returns:
        The JSON data for the new user.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["username", "email", "password"]):
        return errors.missing_registration_parameters()

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    # Ensure that this username can be used
    username_error = validate_username(username)
    if username_error is not None:
        return username_error

    # Ensure that this email address can be used
    email_error = validate_email(email)
    if email_error is not None:
        return email_error

    # Ensure that this password can be used
    password_error = validate_password(password, [username, email])
    if password_error is not None:
        return password_error

    invitation = Invitation.query.filter_by(email=email).first()

    # Make sure this user has received an invitation
    if invitation is None:
        return errors.registration_is_disabled()
    else:
        Invitation.query.filter_by(email=email).delete()

    # Hash the password with bcrypt, this is what we'll save to MySQL
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Create this user in the database
    user = User(username, email, hashed_password)
    db.session.add(user)
    db.session.commit()

    # Add an email verification object to the database, to be deleted when the
    # user clicks the link in their inbox
    verification = EmailVerification(user.id, user.email)
    db.session.add(verification)
    db.session.commit()

    # Send the verification email
    send(Email.VERIFY_EMAIL, user, verification)

    # Log the user into the account they just created
    login_user(user, remember=True)

    # Return JSON data about the new account
    return get_user(user.id)

@mod_users.route("/<user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """Updates a user's settings.

    Args:
        user_id: The id of the user whose settings are being updated.

    Body:
        section: The settings section that is being updated.
        data: The new settings data for the specified section.

    Returns:
        The JSON data for the user whose settings have been updated.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["section", "data"]):
        return errors.missing_update_parameters()

    section = request.json["section"]
    data = request.json["data"]

    # Retrieve the user who is being updated
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        # Return 404 if this user doesn't exist
        return errors.user_not_found()
    elif user.id != current_user.id and not current_user.is_admin:
        # Only the authenticated user and admins can update a user's settings
        return errors.not_authorized()

    # Get the settings that need to be updated
    settings = user.get_settings()

    if section not in settings:
        # Ensure that the settings section is valid
        return errors.invalid_settings_section()
    elif section == "profile":
        # Handle username correctly if the profile section is being updated
        if "username" in data and data["username"] != user.username:
            username = data["username"]

            # Ensure that this username can be used
            username_error = validate_username(username)
            if username_error is not None:
                return username_error

            # Set the user's new username
            user.username = username

        # Handle email correctly if the profile section is being updated
        if "email" in data and data["email"] != user.email:
            email = data["email"]

            # Ensure that this email address can be used
            email_error = validate_email(email)

            if email_error is not None:
                return email_error

            # Set the user's new email address
            user.pending_email = email

            # Add an email verification object to the database, to be deleted
            # when the user clicks the link in their inbox
            verification = EmailVerification(user.id, email)
            db.session.add(verification)
            db.session.commit()

            # Send the verification email
            send(Email.VERIFY_EMAIL, user, verification)

        settings[section] = {
            "first_name": data["first_name"],
            "last_name": data["last_name"]
        }
    else:
        # Just set the data for this section for all other sections
        settings[section] = data

    # Update the user's settings in MySQL
    user.settings = json.dumps(settings)
    db.session.commit()

    # Return this user's JSON data
    return get_user(user.id)

@mod_users.route("/login", methods=["POST"])
def login():
    """Logs in a user with the correct credentials.

    Body:
        username: The username or email address of the user logging in.
        password: The user's password.

    Returns:
        JSON data for the user who just logged in.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["username", "password"]):
        return errors.missing_login_parameters()

    username = request.json["username"]
    password = request.json["password"]

    # Retrieve the user with the correct username or email address
    user = User.query.filter((User.username == username) | (User.email == username)).first()

    # Return 401 if there is no user with this username or email
    if user is None:
        return errors.invalid_credentials()

    # Check if the password is correct
    password_is_correct = bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))

    if password_is_correct:
        # Set the session correctly and return this user's JSON data
        login_user(user, remember=True)
        return get_user(user.id)
    else:
        # Return 401 if the password is incorrect
        return errors.invalid_credentials()

@mod_users.route("/current", methods=["GET"])
@login_required
def get_current_user():
    """Retrieve data about the user who is currently logged in.

    Returns:
        JSON data about the authenticated user, or 401 if nobody is logged in.
    """

    # Return user data if someone is logged in
    return get_user(current_user.id)

@mod_users.route("/current", methods=["DELETE"])
def logout():
    """Logs a user out.

    Returns:
        204 no content.
    """

    logout_user()
    return ("", 204)

@mod_users.route("/<user_id>/password", methods=["PUT"])
@login_required
def update_password(user_id):
    """Updates a user's password.

    Args:
        user_id: The id of the user who is updating their password.

    Body:
        current_password: The user's current password.
        new_password: The password the user would like to change it to.

    Returns:
        The user's JSON data.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["current_password", "new_password"]):
        return errors.missing_password_update_parameters()

    current_password = request.json["current_password"]
    new_password = request.json["new_password"]

    # Retrieve the user who is being updated
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        # Return 404 if this user doesn't exist
        return errors.user_not_found()
    elif user.id != current_user.id:
        # Only the authenticated user can update their password
        return errors.not_authorized()

    # Use bcrypt to check if the current password is correct
    current_password_is_correct = bcrypt.checkpw(current_password.encode("utf-8"), user.password.encode("utf-8"))

    # Return 400 if the current password is incorrect
    if not current_password_is_correct:
        return errors.incorrect_password()

    # Ensure that this password can be used
    password_error = validate_password(new_password, [user.username, user.email])
    if password_error is not None:
        return password_error

    # Hash the new password, this is what will be stored in MySQL
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    # Make the update to this user and save to MySQL
    user.password = hashed_password
    db.session.commit()

    # Return this user's JSON data
    return get_user(user.id)

@mod_users.route("/password/reset", methods=["POST"])
def reset_password():
    """Initiates a forgot password request.

    Body:
        username: The username or email address of the user who needs to reset
            their password.

    Returns:
        204 no content, so account info isn't leaked.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["username"]):
        return errors.missing_password_reset_parameters()

    username = request.json["username"]

    # Retrieve the user with this username or email address
    user = User.query.filter((User.username == username) | (User.email == username)).first()

    # Create a password request code and save in MySQL
    reset = PasswordReset(user)
    db.session.add(reset)
    db.session.commit()

    # Send this user an email with a link to reset their password
    send(Email.FORGOT_PASSWORD, user, reset)

    # Return no content so people can't use this endpoint to check if a
    # particular email address has been used to register an account
    return ("", 204)

@mod_users.route("/email/verify", methods=["PATCH"])
def verify_email():
    """Verifies an email address.

    Body:
        code: The code sent to the inbox of the email being verified.

    Returns:
        204 no content.
    """

    # Check that all necessary data is in the request body
    if not check_body(request, ["code"]):
        return errors.missing_verify_email_parameters()

    code = request.json["code"]

    # Look up the verification object with this code
    verification = EmailVerification.query.filter_by(code=code).first()

    if verification is None:
        # Return 400 if the verification code is invalid
        return errors.invalid_verification_code()

    user = User.query.filter_by(id=verification.user_id).first()

    if user is None:
        # This should never happen, in theory
        log_error("User from verification code doesn't exist")
        return errors.invalid_verification_code()

    # Make sure the user hasn't changed their email address since this verification was initiated
    if user.pending_email != verification.email:
        return errors.incorrect_verification_email()

    # Set the user to verified and delete the verification object
    user.email = user.pending_email
    user.pending_email = None
    db.session.delete(verification)
    db.session.commit()

    return ("", 204)

@mod_users.route("/<user_id>/confirm", methods=["POST"])
@login_required
def resend_confirmation_email(user_id):
    """Resends a confirmation email used to verify a user's email address.

    Args:
        user_id: The user whose id needs the new confirmation email.

    Returns:
        204 no content.
    """

    # Find the user who is confirming their email address
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        # Return 404 if this user doesn't exist
        return errors.user_not_found()

    if not user.pending_email:
        # Return 400 if there is no email address the user needs to confirm
        return errors.no_pending_email()

    # Add an email verification object to the database, to be deleted when the
    # user clicks the link in their email
    verification = EmailVerification(user.id, user.pending_email)
    db.session.add(verification)
    db.session.commit()

    # Send the verification email
    send(Email.VERIFY_EMAIL, user, verification)

    return ("", 204)

@mod_users.route("/<user_id>/confirm", methods=["DELETE"])
@login_required
def cancel_email_change(user_id):
    """Cancels any attempts to update the user's email address.

    Args:
        user_id: The id of the user who wants to cancel their email update.

    Returns:
        204 no content.
    """

    # Find the user who is confirming their email address
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        # Return 404 if this user doesn't exist
        return errors.user_not_found()

    if user.pending_email and user.email == user.pending_email:
        # Return 400 if the user is trying to cancel their first email verification
        return errors.must_confirm_email()

    # Remove all verification attempts for this user
    EmailVerification.query.filter_by(user_id=user.id).delete()

    # Remove the user's pending email address
    user.pending_email = None
    db.session.commit()

    return ("", 204)

@mod_users.route("/invite", methods=["POST"])
@admin_required
def invite_user():
    """Invites a user to register on Storytime.

    Parameters:
        email: The email of the user who needs an invitation.

    Returns:
        204 no content.
    """

    # Ensure necessary parameters are here
    if not check_body(request, ["email"]):
        return errors.missing_invite_parameters()

    email = request.json["email"]

    # See if a user exists with this email address
    user = User.query.filter_by(email=email).first()

    if user is not None:
        # Return 400 if a user exists with this email
        return errors.user_already_exists()

    # Remove all existing invitations to this user
    Invitation.query.filter_by(email=email).delete()

    # Create invitation and add to database
    invitation = Invitation(email)
    db.session.add(invitation)
    db.session.commit()

    # Send the invitation email
    send(Email.INVITE, email_address=email)

    return ("", 204)
