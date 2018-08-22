from flask import request

def check_body(keys):
    if request.json == None:
        return False
    else:
        for key in keys:
            if key not in request.json:
                return False

    return True
