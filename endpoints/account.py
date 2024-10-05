from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
import traceback
from utils import return_response

account = Blueprint('account', __name__)

AUTH_URL_PREFIX = "/account"


# dashboard
@account.route(f"{AUTH_URL_PREFIX}/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    try:
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Welcome to your dashboard"
        )
    except Exception as e:
        print(traceback.format_exc(), "dashboard traceback")
        print(e, "dashboard error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )


# create user
@account.route(f"{AUTH_URL_PREFIX}/create-user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="User created"
        )

    except Exception as e:
        print(traceback.format_exc(), "create user traceback")
        print(e, "create user error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )


# change password
@account.route(f"{AUTH_URL_PREFIX}/change-password", methods=["PATCH"])
@jwt_required()
def change_password():
    try:
        data = request.get_json()

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Password changed"
        )

    except Exception as e:
        print(traceback.format_exc(), "change password traceback")
        print(e, "change password error")
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid data"
        )
