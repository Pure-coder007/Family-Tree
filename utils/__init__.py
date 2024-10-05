from flask import jsonify
from flask_jwt_extended import create_access_token


def return_response(status_code, status=None, message=None, **data):
    res_data = {
        "status": status,
        "message": message
    }
    res_data.update(data)
    
    return jsonify(res_data), status_code


def return_access_token(identity):
    access_token = create_access_token(identity=identity)
    return access_token
