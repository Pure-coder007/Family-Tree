class Config:
    SECRET_KEY = "hard_to_guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "hatrd_to_guess"
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'


config_obj = {
    "development": DevelopmentConfig
}