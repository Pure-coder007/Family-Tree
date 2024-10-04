from flask import Flask
from extensions import jwt, cors, db, migrate
from config import config_obj
from endpoints import AuthBlp
from http_status import HttpStatus
from status_res import StatusRes
from utils import return_response


def create_app(config_name="development"):
    app = Flask(__name__)
    
    app.config.from_object(config_obj[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PATCH", "PUT", "DELETE"],
                "allow_headers": ["Authorization", "Content-Type"],
                "supports_credentials": True,
            }
        },
    )

    # if endpoint does not exist
    @app.errorhandler(404)
    def not_found(error):
        print("error: ", error)
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Endpoint not found"
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        print("error: ", error)
        return return_response(
            HttpStatus.METHOD_NOT_ALLOWED,
            status=StatusRes.FAILED,
            message="Method not allowed"
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        print("error: ", error)
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error"
        )
    
    app.register_blueprint(AuthBlp, url_prefix="/api/v1")
    
    return app
