from flask import jsonify
from flask_jwt_extended import create_access_token
import random
import uuid
import hmac
import hashlib
import base64
from io import BytesIO
import time


def hex_uuid():
    return str(uuid.uuid4().hex)


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


def generate_otp():
    return str(random.randint(100000, 999999))


def convert_binary(base64_file):
    try:
        print("got here")
        binary_data = base64.b64decode(base64_file)
        # Convert binary data to a file-like object
        file_like = BytesIO(binary_data)
        print(file_like, "file_like from convert_binary")
        return file_like
    except Exception as e:
        print(e, "error from convert_binary")
        return None


def generate_signature(params_to_sign, api_secret):
    try:
        params_to_sign['timestamp'] = int(time.time())
        sorted_params = '&'.join([f'{k}={params_to_sign[k]}' for k in sorted(params_to_sign)])
        to_sign = f'{sorted_params}{api_secret}'
        signature = hmac.new(api_secret.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha1).hexdigest()
        print(signature, "signature from generate_signature")
        return signature
    except Exception as e:
        print(e, "error from generate_signature")
        return None


def validate_request_data(data, required_fields):
    for field in required_fields:
        if not data.get(field):
            return False, f"{field} is required"
    return True, None
