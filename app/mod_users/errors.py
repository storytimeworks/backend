def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def invalid_credentials():
    return error(401, 101, "Invalid login credentials")

def missing_authentication():
    return error(401, 102, "Missing authentication")

def user_not_found():
    return error(404, 103, "User not found")

def missing_registration_parameters():
    return error(400, 104, "Missing necessary registration parameters")

def short_username():
    return error(400, 105, "Username must be at least four characters long")

def long_username():
    return error(400, 106, "Username must be 16 characters or fewer")

def no_dash_start_username():
    return error(400, 107, "Username can't start with a dash or underscore")

def invalid_username():
    return error(400, 108, "Username must only contain letters, numbers, dashes, and underscores")

def weak_password(suggestions):
    return error(400, 109, "Password is too weak", suggestions)

def username_taken():
    return error(409, 110, "Username is already taken")

def email_used():
    return error(409, 111, "Email has already been used")

def invalid_email():
    return error(400, 112, "Email address is invalid")

def missing_login_parameters():
    return error(400, 113, "Missing necessary login parameters")