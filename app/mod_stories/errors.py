def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def story_not_found():
    return error(404, 1601, "The story could not be found")

def missing_create_story_parameters():
    return error(400, 1602, "Missing parameters needed to create a story")

def missing_update_story_parameters():
    return error(400, 1603, "Missing parameters needed to update a story")
