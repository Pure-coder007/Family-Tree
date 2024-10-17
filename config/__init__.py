# import os
# import pymysql  
# from dotenv import load_dotenv
# from extensions import db
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# import os
# from dotenv import load_dotenv

# load_dotenv()

# base_dir = os.path.abspath(os.path.dirname(__file__))


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
#     JWT_ACCESS_TOKEN_EXPIRES = 86400
    

# class DevelopmentConfig(Config):
#     DEBUG = True
#     # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "db.sqlite3")
#     SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@db4free.net/my_familytree"


# config_obj = {
#     "development": DevelopmentConfig
# }







import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Base directory for the application
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configuration class for the app
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 86400

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    # Setup MySQL database URI using the environment variables
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}"
        f"@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

# Config dictionary to choose the environment
config_obj = {
    "development": DevelopmentConfig
}

# Set configuration for the app
app.config.from_object(config_obj['development'])

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Example route
@app.route('/')
def home():
    return "Connected  successfully!"

if __name__ == '__main__':
    app.run(debug=True)

