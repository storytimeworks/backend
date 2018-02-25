def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def missing_authentication():
    return error(401, 201, "Missing authentication")

def not_authorized():
    return error(401, 202, "Not authorized to perform this action")

def invalid_session():
    return error(400, 203, "Invalid session")
