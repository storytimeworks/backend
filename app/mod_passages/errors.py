def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def passage_not_found():
    return error(404, 1503, "The passage could not be found")

def missing_create_passage_parameters():
    return error(400, 1504, "Missing parameters needed to create a passage")

def missing_update_passage_parameters():
    return error(400, 1505, "Missing parameters needed to update a passage")

def passage_not_reached():
    return error(403, 1506, "You haven't unlocked this passage yet")
