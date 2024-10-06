from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
import traceback
from utils import return_response
from models import (get_family_names, create_family_name,
                    create_user, email_or_phone_exists, get_all_users)
from decorators import super_admin_required

account = Blueprint('account', __name__)

ACCOUNT_URL_PREFIX = "/account"


# dashboard
@account.route(f"{ACCOUNT_URL_PREFIX}/dashboard", methods=["GET"])
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
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get family names
@account.route(f"{ACCOUNT_URL_PREFIX}/family-names", methods=["GET"])
@jwt_required()
@super_admin_required
def family_names():
    try:
        fam_names = get_family_names()
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Family names retrieved", family_names=fam_names
        )
    except Exception as e:
        print(traceback.format_exc(), "family names traceback")
        print(e, "family names error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# create user
@account.route(f"{ACCOUNT_URL_PREFIX}/create-user", methods=["POST"])
@jwt_required()
@super_admin_required
def create_fam_user():
    try:
        data = request.get_json()

        # Define required and optional fields
        required_fields = ["email", "password", "first_name", "last_name",
                           "gender", "img_str", "phone_number", "dob"]
        optional_fields = {
            "is_super_admin": False,
            "family_name": None,
            "family_id": None,
        }

        # Validate required fields
        for key in required_fields:
            if not data.get(key):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message=f"{key} is required"
                )

        if data.get("gender") not in ("Male", "Female"):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gender must be either Male or Female"
            )

        if email_or_phone_exists(email=data.get("email")):
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="Email already exists"
            )

        if email_or_phone_exists(phone_number=data.get("phone_number")):
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="Phone number already exists"
            )

        # Extract optional fields
        family_id = data.get("family_id")
        fam_name = data.get("family_name")

        if not family_id and not fam_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Family name is required"
            )

        if family_id and fam_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="You can't select family name and provide a new one"
            )

        # Create family name if provided
        if fam_name:
            fam = create_family_name(fam_name)

        # Create user
        create_user(
            email=data.get("email"),
            password=data.get("password"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            gender=data.get("gender"),
            img_str=data.get("img_str"),
            is_super_admin=data.get("is_super_admin", False),
            family_name=fam.id if fam_name else family_id,
            phone_number=data.get("phone_number"),
            dob=data.get("dob"),
            status=data.get("status", "Alive"),
            deceased_at=data.get("deceased_at")
        )

        return return_response(
            HttpStatus.CREATED,
            status=StatusRes.SUCCESS,
            message="User created"
        )

    except Exception as e:
        print(traceback.format_exc(), "create user traceback")
        print(e, "create user error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get all users
@account.route(f"{ACCOUNT_URL_PREFIX}/all-users", methods=["GET"])
@jwt_required()
def all_users():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        fullname = request.args.get("fullname")
        email = request.args.get("email")
        family_id = request.args.get("family_id")
        users = get_all_users(page, per_page, fullname, email, family_id)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="All users retrieved", data={
                "users": [user.to_dict() for user in users.items],
                "total_items": users.total,
                "page": users.page,
                "per_page": users.per_page,
                "total_pages": users.pages,
            }
        )
    except Exception as e:
        print(traceback.format_exc(), "all users traceback")
        print(e, "all users error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# change password
@account.route(f"{ACCOUNT_URL_PREFIX}/change-password", methods=["PATCH"])
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
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )
