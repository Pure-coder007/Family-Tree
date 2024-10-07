from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum
import re
import datetime
from utils import hex_uuid
# from datetime import datetime
from datetime import datetime, timedelta



class Gender(Enum):
    male = "Male"
    female = "Female"


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


class Status(Enum):
    alive = "Alive"
    deceased = "Deceased"


class FamilyName(db.Model):
    __tablename__ = "family_names"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship("User", backref="family", lazy=True)

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
    dob = db.Column(db.DateTime, nullable=True)
    status = db.Column(SQLAlchemyEnum(Status), default=Status.alive)
    deceased_at = db.Column(db.DateTime, nullable=True)
    img_str = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(25), nullable=True)
    password = db.Column(db.Text, nullable=False)
    family_name = db.Column(db.String(50), db.ForeignKey("family_names.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    user_session = db.relationship("UserSession", backref="user", lazy=True, uselist=False)

    def __init__(self, email, password, first_name,
                 last_name, gender, is_super_admin, img_str=None,
                 family_name=None, phone_number=None, dob=None, status=None, deceased_at=None):
        self.email = email
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender.title())
        self.is_super_admin = is_super_admin
        self.family_name = family_name
        self.img_str = img_str
        self.phone_number = phone_number
        self.dob = dob
        self.status = Status(status) if status else Status.alive
        self.deceased_at = deceased_at

    def to_dict(self):
        user_dict = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "gender": self.gender.value,
            "is_super_admin": self.is_super_admin,
            "img_str": self.img_str,
            "family_name": self.family.name.title() if self.family_name else None,
            "phone_number": self.phone_number,
            "dob": self.dob.strftime("%d-%b-%Y") if self.dob else None,
            "status": self.status.value,
            "deceased_at": self.deceased_at,
        }
        return {key: value for key, value in user_dict.items() if value}

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
                gender, img_str, is_super_admin=False, family_name=None, phone_number=None,
                dob=None, status=None, deceased_at=None):
    user = User(email=email, password=password, first_name=first_name,
                last_name=last_name, gender=gender, img_str=img_str,
                is_super_admin=is_super_admin, family_name=family_name,
                phone_number=phone_number, dob=dob, status=status, deceased_at=deceased_at)
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
            user_session.otp_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, otp=otp,
                                       otp_expires_at=datetime.now() + timedelta(minutes=10))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    elif token:
        user_session = UserSession.query.filter_by(user_id=user_id).first()
        if user_session:
            user_session.token = token
            user_session.token_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(user_id=user_id, token=token,
                                       token_expires_at=datetime.now() + timedelta(minutes=10))
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


def get_all_users(page, per_page, fullname, email, family_id):
    users = User.query
    if fullname:
        users = users.filter(
            db.or_(
                User.first_name.ilike(f"%{fullname}%"),
                User.last_name.ilike(f"%{fullname}%")
            )
        )
    if email:
        users = users.filter(User.email.ilike(f"%{email}%"))
    if family_id:
        users = users.filter(User.family_name == family_id)
    users = users.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return users


# Getting all users under one family name
def get_family_users(family_id):
    users = User.query.filter(User.family_name == family_id)
    if not users:
        return "No users found"
    return [user.to_dict() for user in users]



# Update user
def update_user(user_id,  **kwargs):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return False
    
    # Update user attributes with provided keyword arguments
    user.first_name = kwargs.get("first_name") or user.first_name
    user.last_name = kwargs.get("last_name") or user.last_name
    user.password = kwargs.get("password") or user.password
    user.gender = kwargs.get("gender") or user.gender
    user.img_str = kwargs.get("img_str") or user.img_str
    user.status = kwargs.get("status") or user.status
    user.email = kwargs.get("email") or user.email
    
    
    # Handle date of birth conversion
    dob_input = kwargs.get("dob")
    if dob_input:
        try:
            user.dob = datetime.strptime(dob_input, '%d-%m-%Y').date()  # Convert to date
        except ValueError:
            return "Invalid date format. Please use DD-MM-YYYY."
    else:
        user.dob = user.dob  # Keep existing value if no new value is provided

    user.deceased_at = kwargs.get("deceased_at") or user.deceased_at
    user.phone_number = kwargs.get("phone_number") or user.phone_number
    user.family_name = kwargs.get("family_name") or user.family_name
    user.family_id = kwargs.get("family_id") or user.family_id
    # hash password
    user.password = hasher.hash(user.password)
    
    db.session.commit()
    # return user
    users = User.query.filter(User.family_name == family_id).all()
    return [user.to_dict() for user in users]
