from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint, request
from utils import return_response, return_access_token
from models import verify_user_login

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
    email = request.json.get("email")
    password = request.json.get("password")
    if not email or not password:
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Email and password are required"
        )
    user = verify_user_login(email, password)
    if not user:
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Invalid credentials"
        )
    access_token = return_access_token(user.id)
    return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Login successful", access_token=access_token
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
