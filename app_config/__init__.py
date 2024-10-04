from flask import Flask
from extensions import jwt, cors, db, migrate
from config import config_obj
from endpoints import AuthBlp


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
    
    app.register_blueprint(AuthBlp, url_prefix="/api/v1")
    
    return app
