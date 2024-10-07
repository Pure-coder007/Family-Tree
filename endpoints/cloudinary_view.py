from flask import Blueprint, request
import cloudinary.uploader
import cloudinary.api
import cloudinary_config
from utils import convert_binary, generate_signature, return_response
from http_status import HttpStatus
from status_res import StatusRes
import time
import os
import traceback
from dotenv import load_dotenv

cloudnary = Blueprint("cloudnary", __name__)

ACCOUNT_PREFIX = "cloudinary"


load_dotenv()


@cloudnary.route(f"/{ACCOUNT_PREFIX}/manage-image", methods=["POST"])
def manage_file():
    try:
        data = request.get_json()
        image = data.get("image", None)
        public_id = data.get("public_id", None)
        action = data.get("action", None)
        folder = data.get("folder", None)

        print(data, "data")

        cloud_name = (os.environ.get("CLOUD_NAME"),)
        api_key = (os.environ.get("API_KEY"),)
        api_secret = (os.environ.get("API_SECRET"),)

        cloud_name = str(cloud_name[0]) if isinstance(cloud_name, tuple) else cloud_name
        api_key = str(api_key[0]) if isinstance(api_key, tuple) else api_key
        api_secret = str(api_secret[0]) if isinstance(api_secret, tuple) else api_secret

        print("cloud_name", cloud_name)
        print("api_key", api_key)
        print("api_secret", api_secret)

        if not action:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Action is required",
            )

        if action == "upload" and not image:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="File is required",
            )

        if not public_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Public ID is required",
            )

        file = convert_binary(image) if action == "upload" else None

        print("file", file)

        params_to_sign = {
            "public_id": public_id,
            "timestamp": int(time.time()),
        }
        signature = generate_signature(params_to_sign, api_secret)

        params_to_sign["signature"] = signature

        print(signature, "signature from cloudinary")
        print(params_to_sign, "params_to_sign from cloudinary")

        params_to_sign["folder"] = folder if folder else None

        if action == "upload":
            print(action, "action from cloudinary")
            result = cloudinary.uploader.upload(file, **params_to_sign)
            print(result, "result from cloudinary")
            img_url = result["secure_url"]

            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="File uploaded successfully",
                data={
                    "img_url": img_url,
                    "public_id": public_id,
                    "signature": signature,
                },
            )
        elif action == "destroy":
            params_to_sign["public_id"] = (
                f"{folder}/{public_id}" if folder else public_id
            )
            result = cloudinary.uploader.destroy(**params_to_sign)
            print(params_to_sign, "pparams")
            print(result, "result from cloudinary destroy")

            return (
                return_response(
                    HttpStatus.OK,
                    status=StatusRes.SUCCESS,
                    message="Image deleted successfully",
                )
                if result["result"] == "ok"
                else return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Image not found",
                )
            )
        else:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid action",
            )

    except KeyError as e:
        print(e, "error from cloudinary key error")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="All fields are required",
        )
    except Exception as e:
        print(traceback.format_exc(), "error from cloudinary exception")
        print(e, "error from cloudinary")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network error",
        )
