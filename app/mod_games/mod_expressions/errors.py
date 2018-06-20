def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def missing_create_question_parameters():
    return error(400, 1801, "Missing parameters needed to create a question")
