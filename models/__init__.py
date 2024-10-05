from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum
import re


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
    is_super_admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    user_session = db.relationship("UserSession", backref="user", lazy=True, uselist=False)

    def __init__(self, email, password, first_name, last_name, gender):
        self.email = email
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender)

    def update_password(self, new_password):
        self.password = hasher.hash(new_password)

    @staticmethod
    def validate_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def __repr__(self):
        return f"<User {self.username}>"


class UserSession(db.Model):
    __tablename__ = "user_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<UserSession {self.user_id}>"


def create_user(email, password, first_name, last_name, gender):
    user = User(email, password, first_name, last_name, gender)
    db.session.add(user)
    db.session.commit()
    return user


def verify_user_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and hasher.verify(password, user.password):
        return user
    return False


def create_otp_token(user_id, otp=None, token=None):
    if otp:
        user_session = UserSession.query.filter_by(user_id=user_id).first()
        if user_session:
            user_session.otp = otp
            user_session.otp_expires_at = db.func.now() + db.func.interval(10, "minute")
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, otp=otp, otp_expires_at=db.func.now() + db.func.interval(10, "minute"))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    elif token:
        user_session = UserSession.query.filter_by(user_id=user_id).first()
        if user_session:
            user_session.token = token
            user_session.token_expires_at = db.func.now() + db.func.interval(1, "day")
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, token=token, token_expires_at=db.func.now() + db.func.interval(1, "day"))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    return None


def get_user_by_email(email):
    user = User.query.filter_by(email=email.lower()).first()
    return user


def valid_email(email):
    return User.validate_email(email)
