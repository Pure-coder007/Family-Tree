from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required
import traceback
from utils import return_response, validate_request_data
from models import (edit_member, email_exists, Moderators,
                    get_all_members, create_member_with_spouse,
                    create_mod, get_family_chain, change_password,
                    get_all_mods, update_mod, get_one_fam_member)
from decorators import super_admin_required
import datetime
import pprint
from flask_jwt_extended import current_user
import logging


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


# create member
@account.route(f"{ACCOUNT_URL_PREFIX}/create-member", methods=["POST"])
@jwt_required()
@super_admin_required
def create_fam_member():
    try:
        data = request.get_json()

        pprint.pprint(data)
        gender = data.get("gender")
        dob = data.get("dob")
        deceased_at = data.get("deceased_at")

        required_fields = ["first_name", "last_name", "gender", "dob", "status",
                           "img_str", "birth_place", "birth_name"]
        valid, message = validate_request_data(data, required_fields)

        if not valid:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=message
            )

        if gender not in ["Male", "Female"]:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid gender"
            )

        if data.get("deceased_at") and data.get("status") != "Deceased":
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Only deceased members can have a deceased date"
            )

        if data.get("status") == "Deceased" and not data.get("deceased_at"):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Deceased date is required"
            )

        try:
            data["dob"] = datetime.datetime.strptime(dob, "%d-%m-%Y").date() if dob else None
            data["deceased_at"] = datetime.datetime.strptime(deceased_at, "%d-%m-%Y").date() if deceased_at else None
        except ValueError as e:
            print(traceback.format_exc(), "create member traceback")
            print(e, "create member error")
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid date format"
            )

        res, err = create_member_with_spouse(data)
        if err:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message=err
            )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Member created successfully"
        )

    except Exception as e:
        print(traceback.format_exc(), "create member traceback")
        print(e, "create member error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# edit fam member
@account.route(f"{ACCOUNT_URL_PREFIX}/edit-member/<member_id>", methods=["POST"])
@jwt_required()
@super_admin_required
def edit_fam_member(member_id):
    try:
        data = request.get_json()
        try:
            if data.get("dob"):
                data["dob"] = datetime.datetime.strptime(data["dob"], "%d-%m-%Y").date()
            if data.get("deceased_at"):
                data["deceased_at"] = datetime.datetime.strptime(data["deceased_at"], "%d-%m-%Y").date()
        except ValueError as e:
            print(traceback.format_exc(), "create member traceback")
            print(e, "create member error")
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid date format"
            )

        if data.get("status") == "Deceased" and not data.get("deceased_at"):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Deceased date is required"
            )

        if data.get("deceased_at") and data.get("status") != "Deceased":
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Only deceased members can have a deceased date"
            )

        if data.get("gender") and data.get("gender") not in ["Male", "Female"]:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid gender, must be Male or Female"
            )

        if data.get("other_spouses") and not isinstance(data.get("other_spouses"), list):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Other spouse must be an array"
            )

        if data.get("children") and not isinstance(data.get("children"), list):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Children must be an array"
            )

        edit_member(member_id, data)

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Member updated successfully"
        )
    except Exception as e:
        print(traceback.format_exc(), "edit member traceback")
        print(e, "edit member error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get all members
@account.route(f"{ACCOUNT_URL_PREFIX}/all-members", methods=["GET"])
@jwt_required()
def all_members():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        fullname = request.args.get("fullname")
        members = get_all_members(page, per_page, fullname)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="All members retrieved", data={
                "members": [member.to_dict() for member in members.items],
                "total_items": members.total,
                "page": members.page,
                "per_page": members.per_page,
                "total_pages": members.pages,
            }
        )
    except Exception as e:
        print(traceback.format_exc(), "all members traceback")
        print(e, "all members error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get one member
@account.route(f"{ACCOUNT_URL_PREFIX}/member/<member_id>", methods=["GET"])
@jwt_required()
def get_one_member(member_id):
    try:
        member = get_family_chain(member_id)
        if not member:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Member not found"
            )
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Member retrieved", **member
        )
    except Exception as e:
        print(traceback.format_exc(), "get one member traceback")
        print(e, "get one member error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get one fam member
@account.route(f"{ACCOUNT_URL_PREFIX}/fam-member/<member_id>", methods=["GET"])
@jwt_required()
def get_one_fam(member_id):
    try:
        member = get_one_fam_member(member_id)
        if not member:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Member not found"
            )
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Member retrieved", **member
        )
    except Exception as e:
        print(traceback.format_exc(), "get one member traceback")
        print(e, "get one member error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# create mod
@account.route(f"{ACCOUNT_URL_PREFIX}/create-mod", methods=["POST"])
@jwt_required()
@super_admin_required
def create_moderator():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        is_super_admin = data.get("is_super_admin", False)
        fullname = data.get("fullname")

        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required"
            )

        if not fullname:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Name is required"
            )
        if not password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Password is required"
            )

        email = email.lower()

        if not Moderators.validate_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid email"
            )

        res = email_exists(data.get("email"))
        if res:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already exists"
            )
        create_mod(email, password, fullname, is_super_admin)

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Moderator created"
        )

    except Exception as e:
        print(traceback.format_exc(), "create mod traceback")
        print(e, "create mod error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# get al mods
@account.route(f"{ACCOUNT_URL_PREFIX}/all-mods", methods=["GET"])
@jwt_required()
@super_admin_required
def all_moderators():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        fullname = request.args.get("fullname")
        email = request.args.get("email")
        mods = get_all_mods(page, per_page, fullname, email)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="All mods retrieved", **{
                "mods": [mod.to_dict() for mod in mods.items],
                "total_items": mods.total,
                "page": mods.page,
                "per_page": mods.per_page,
                "total_pages": mods.pages,
            }
        )
    except Exception as e:
        print(traceback.format_exc(), "all mods traceback")
        print(e, "all mods error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# edit mod
@account.route(f"{ACCOUNT_URL_PREFIX}/edit-mod/<mod_id>", methods=["PATCH"])
@jwt_required()
@super_admin_required
def edit_moderator(mod_id):
    try:
        data = request.get_json()

        pprint.pprint(data)

        if data.get("status") and data.get("status") not in ["active", "inactive"]:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid status"
            )

        res = update_mod(mod_id, **data)

        if not res:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Moderator not found"
            )

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Moderator updated"
        )

    except Exception as e:
        print(traceback.format_exc(), "edit mod traceback")
        print(e, "edit mod error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# delete mod
@account.route(f"{ACCOUNT_URL_PREFIX}/delete-mod/<mod_id>", methods=["DELETE"])
@jwt_required()
@super_admin_required
def delete_moderator(mod_id):
    try:
        res = update_mod(mod_id, delete=True)

        if not res:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Moderator not found"
            )
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Moderator deleted"
        )

    except Exception as e:
        print(traceback.format_exc(), "delete mod traceback")
        print(e, "delete mod error")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )


# change password
@account.route(f"{ACCOUNT_URL_PREFIX}/change-password", methods=["PATCH"])
@jwt_required()
def change_password_route():
    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not old_password:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Old password is required"
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

        if not change_password(current_user.id, old_password, new_password):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Incorrect old password"
            )

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Password changed"
        )

    except Exception as e:
        logging.error("Change password error: %s", e)
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )
