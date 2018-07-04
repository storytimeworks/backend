def error(status_code, code, message, data=None):
    from flask import jsonify
    if data is None:
        return (jsonify(code=code, message=message), status_code)
    else:
        return (jsonify(code=code, message=message, data=data), status_code)

def missing_answer_parameters():
    return error(400, 2001, "Missing answer parameters")

def missing_train_parameters():
    return error(400, 2002, "Missing train parameters")

def invalid_classification():
    return error(400, 2003, "Classification must be 0-10")
