def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def question_not_found():
    return error(404, 2101, "Question could not be found")

def missing_create_question_parameters():
    return error(400, 2102, "Missing parameters needed to create a question")

def missing_update_question_parameters():
    return error(400, 2103, "Missing parameters needed to update a question")
