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
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    
    app.register_blueprint(AuthBlp)
    
    return app
