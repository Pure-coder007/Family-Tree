from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum
import re
import datetime
from utils import hex_uuid


class Gender(Enum):
    M = "Male"
    F = "Female"


class RelationshipType(Enum):
    wife = "Wife"
    ex_wife = "Ex-Wife"
    husband = "Husband"
    ex_husband = "Ex-Husband"
    partner = "Partner"
    ex_partner = "Ex-Partner"
    secondary_wife = "Secondary Wife"


class ChildType(Enum):
    son = "Son"
    daughter = "Daughter"
    step_son = "Step Son"
    step_daughter = "Step Daughter"
    adopted_son = "Adopted Son"
    adopted_daughter = "Adopted Daughter"


class FamilyName(db.Model):
    __tablename__ = "family_names"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship("User", backref="fam_name", lazy=True)

    def __init__(self, name):
        self.name = name.lower()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(SQLAlchemyEnum(Gender))
    is_super_admin = db.Column(db.Boolean, default=False)
    img_str = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(25), nullable=True)
    password = db.Column(db.Text, nullable=False)
    family_name = db.Column(db.String(50), db.ForeignKey("family_names.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    user_session = db.relationship("UserSession", backref="user", lazy=True, uselist=False)

    def __init__(self, email, password, first_name,
                 last_name, gender, is_super_admin, img_str=None,
                 family_name=None, phone_number=None):
        self.email = email
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender.upper())
        self.is_super_admin = is_super_admin
        self.family_name = family_name
        self.img_str = img_str
        self.phone_number = phone_number

    def update_password(self, new_password):
        self.password = hasher.hash(new_password)
        db.session.commit()

    @staticmethod
    def validate_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def __repr__(self):
        return f"<User {self.username}>"


class UserSession(db.Model):
    __tablename__ = "user_sessions"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<UserSession {self.user_id}>"


class Relationship(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    person_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    partner_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    relationship_type = db.Column(SQLAlchemyEnum(RelationshipType))


class Child(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    parent_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    child_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    child_type = db.Column(SQLAlchemyEnum(ChildType))


def create_user(email, password, first_name, last_name,
                gender, img_str, is_super_admin=False, family_name=None, phone_number=None):
    user = User(email=email, password=password, first_name=first_name,
                last_name=last_name, gender=gender, img_str=img_str,
                is_super_admin=is_super_admin, family_name=family_name, phone_number=phone_number)
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
            user_session.otp_expires_at = datetime.datetime.now() + datetime.timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, otp=otp,
                                       otp_expires_at=datetime.datetime.now() + datetime.timedelta(minutes=10))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    elif token:
        user_session = UserSession.query.filter_by(user_id=user_id).first()
        if user_session:
            user_session.token = token
            user_session.token_expires_at = datetime.datetime.now() + datetime.timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, token=token,
                                       token_expires_at=datetime.datetime.now() + datetime.timedelta(minutes=10))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    return None


def get_user_by_email(email):
    user = User.query.filter_by(email=email.lower()).first()
    return user


def valid_email(email):
    return User.validate_email(email)


def create_family_name(name):
    fam = FamilyName.query.filter(
        FamilyName.name.ilike(name)
    ).first()
    if fam:
        return fam
    family_name = FamilyName(name=name)
    db.session.add(family_name)
    db.session.commit()
    return family_name


def get_family_names():
    family_names = FamilyName.query.all()
    return [{"id": fam.id, "name": fam.name.title()} for fam in family_names]


def email_or_phone_exists(email=None, phone_number=None):
    if email:
        return User.query.filter_by(email=email.lower()).first()
    if phone_number:
        return User.query.filter_by(phone_number=phone_number).first()
    return None
