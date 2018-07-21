def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def missing_finish_parameters():
    return error(400, 2201, "Missing finish parameters")

def missing_create_question_parameters():
    return error(400, 2202, "Missing create question parameters")

def question_not_found():
    return error(404, 2203, "Question could not be found with this id")
