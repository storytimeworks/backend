def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def speech_not_found():
    return error(404, 1301, "Recording not found")

def issue_generating_speech():
    return error(500, 1302, "Error searching for recording")

def text_not_provided():
    return error(400, 1303, "No text was given")

def not_generating_speech():
    return error(500, 1304, "No speech is being generated right now")
