def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def app_not_found():
    return error(404, 1701, "The app could not be found")

def missing_create_app_parameters():
    return error(400, 1702, "Missing parameters needed to create an app")

def missing_message_arguments():
    return error(400, 1703, "Missing arguments needed to message an app")
