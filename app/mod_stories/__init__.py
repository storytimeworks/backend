def check_body(request, keys):
    if request.json == None:
        return False
    else:
        for key in keys:
            if key not in request.json:
                return False

    return True
