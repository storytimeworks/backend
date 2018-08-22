def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def question_not_found():
    return error(404, 1401, "Question could not be found")

def missing_create_question_parameters():
    return error(400, 1402, "Missing parameters needed to create a question")

def missing_update_question_parameters():
    return error(400, 1403, "Missing parameters needed to update a question")

def missing_finish_parameters():
    return error(400, 1404, "Missing parameters needed to finish a game")
