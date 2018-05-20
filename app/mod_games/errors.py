def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def missing_attempt_parameters():
    return error(400, 1401, "Missing attempt parameters")

def not_authenticated():
    return error(401, 1402, "Not authenticated")
