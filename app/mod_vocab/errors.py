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

def entry_not_found():
    return error(404, 204, "Entry not found")

def missing_create_entry_parameters():
    return error(400, 205, "Missing parameters needed to create an entry")

def missing_update_entry_parameters():
    return error(400, 206, "Missing parameters needed to update an entry")
