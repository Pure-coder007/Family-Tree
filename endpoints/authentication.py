from http_status import HttpStatus
from status_res import StatusRes
from flask import Blueprint
from utils import return_response

auth = Blueprint('auth', __name__)



@auth.route("/")
def test_endpoint():
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Welcome to the App"
    )
