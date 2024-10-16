from functools import wraps
from flask_jwt_extended import current_user
from utils import return_response
from status_res import StatusRes
from http_status import HttpStatus


# super admin required decorator
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_super_admin:
            return f(*args, **kwargs)
        return return_response(
            HttpStatus.UNAUTHORIZED, status=StatusRes.FAILED, message="Unauthorized"
        )

    return decorated_function
