from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint, request
import traceback
from datetime import datetime
from utils import return_response, return_access_token, generate_otp
from models import verify_user_login, get_user_by_email, valid_email, create_otp_token

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
    try:
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
    except Exception as e:
        print(traceback.format_exc(), "login traceback")
        print(e, "login error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )


# forget password
@auth.route(f"{AUTH_URL_PREFIX}/forget-password", methods=["POST"])
def forget_password():
    try:
        data = request.get_json()

        email = data.get("email")
        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Email is required"
            )
        if not valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid email"
            )
        user = get_user_by_email(email)
        if not user:
            return return_response(
                HttpStatus.NOT_FOUND, status=StatusRes.FAILED, message="User not found"
            )
        otp = generate_otp()
        print(otp, "otp")
        user_session = create_otp_token(user.id, otp=otp)

        # send mail to the user for the otp

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="OTP sent to email",
            email=email
        )
    except Exception as e:
        print(traceback.format_exc(), "forget_password traceback")
        print(e, "forget_password error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )


# reset password
@auth.route(f"{AUTH_URL_PREFIX}/reset-password/<email>", methods=["PATCH"])
def reset_password(email):
    try:
        data = request.get_json()
        otp = data.get("otp")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if not otp:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="OTP is required"
            )
        if not new_password:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="New password is required"
            )
        if not confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Confirm password is required"
            )

        if new_password != confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Passwords do not match"
            )
        if not valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid email"
            )
        user = get_user_by_email(email)
        if not user:
            return return_response(
                HttpStatus.NOT_FOUND, status=StatusRes.FAILED, message="User not found"
            )

        if user.user_session.otp != otp:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid OTP"
            )

        if user.user_session.otp_expires_at < datetime.now():
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="OTP has expired"
            )

        user.update_password(new_password)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Password reset successful"
        )
    except Exception as e:
        print(traceback.format_exc(), "reset_password traceback")
        print(e, "reset_password error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )
