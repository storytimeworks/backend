def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def invalid_credentials():
    return error(401, 1101, "Invalid login credentials")

def user_not_found():
    return error(404, 1103, "User not found")

def missing_registration_parameters():
    return error(400, 1104, "Missing necessary registration parameters")

def short_username():
    return error(400, 1105, "Username must be at least four characters long")

def long_username():
    return error(400, 1106, "Username must be 16 characters or fewer")

def no_dash_start_username():
    return error(400, 1107, "Username can't start with a dash or underscore")

def invalid_username():
    return error(400, 1108, "Username must only contain letters, numbers, dashes, and underscores")

def weak_password(suggestions):
    return error(400, 1109, "Password is too weak", suggestions)

def username_taken():
    return error(409, 1110, "Username is already taken")

def email_used():
    return error(409, 1111, "Email has already been used")

def invalid_email():
    return error(400, 1112, "Email address is invalid")

def missing_login_parameters():
    return error(400, 1113, "Missing necessary login parameters")

def missing_update_parameters():
    return error(400, 1114, "Missing necessary update parameters")

def not_authorized():
    return error(403, 1115, "Not authorized to do this")

def invalid_settings_section():
    return error(400, 1116, "Invalid settings section")

def missing_password_update_parameters():
    return error(400, 1117, "Missing necessary password update parameters")

def incorrect_password():
    return error(400, 1118, "Incorrect password while trying to change password")

def missing_password_reset_parameters():
    return error(400, 1119, "Missing necessary password reset parameters")

def missing_verify_email_parameters():
    return error(400, 1120, "Missing necessary verification parameters")

def invalid_verification_code():
    return error(400, 1121, "The verification code is invalid")

def incorrect_verification_email():
    return error(400, 1122, "You need to send a new verification email to the email address you have set now")
