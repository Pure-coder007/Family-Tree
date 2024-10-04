from flask import jsonify

def return_response(status_code, status=None, message=None, **data):
    res_data = {
        "status": status,
        "message": message
    }
    res_data.update(data)
    
    return jsonify(res_data), status_code
