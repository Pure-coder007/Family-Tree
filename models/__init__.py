from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum


class Gender(Enum):
    M = "Male"
    F = "Female"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(SQLAlchemyEnum(Gender))
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, email, password, first_name, last_name, gender):
        self.email = email
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender)

    def __repr__(self):
        return f"<User {self.username}>"


def create_user(email, password, first_name, last_name, gender):
    user = User(email, password, first_name, last_name, gender)
    db.session.add(user)
    db.session.commit()
    return user


def verify_user_login(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    return hasher.verify(password, user.password)
