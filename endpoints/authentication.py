from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint
from utils import return_response

auth = Blueprint('auth', __name__)

AUTH_URL_PREFIX = "/auth"


@auth.route("/")
def test_endpoint():
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Welcome to the App"
    )


# login
@auth.route(f"{AUTH_URL_PREFIX}/login", methods=["POST"])
def login():
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Login successful"
    )


# forget password
@auth.route(f"{AUTH_URL_PREFIX}/forget-password", methods=["POST"])
def forget_password():
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Forget password successful"
    )


# reset password
@auth.route(f"{AUTH_URL_PREFIX}/reset-password/<email>", methods=["POST"])
def reset_password(email):
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Reset password successful"
    )
