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


class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(SQLAlchemyEnum(Gender))
    dob = db.Column(db.DateTime, nullable=True)
    status = db.Column(SQLAlchemyEnum(Status), default=Status.alive)
    deceased_at = db.Column(db.DateTime, nullable=True)
    img_str = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(25), nullable=True)
    occupation = db.Column(db.String(50), nullable=True)
    birth_place = db.Column(db.String(150), nullable=True)
    birth_name = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, first_name,
                 last_name, gender, img_str=None,
                phone_number=None, dob=None, status=None, deceased_at=None):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender.title())
        self.img_str = img_str
        self.phone_number = phone_number
        self.dob = dob
        self.status = Status(status) if status else Status.alive
        self.deceased_at = deceased_at or None

    def to_dict(self):
        member_dict = {
            "id": self.id,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "gender": self.gender.value,
            "img_str": self.img_str,
            "phone_number": self.phone_number,
            "dob": self.dob.strftime("%d-%b-%Y") if self.dob else None,
            "status": self.status.value,
            "deceased_at": self.deceased_at.strftime("%d-%b-%Y") if self.deceased_at else None,
        }
        return {key: value for key, value in member_dict.items() if value}

    def __repr__(self):
        return f"<Member {self.last_name}>"


class Moderators(db.Model):
    __tablename__ = "moderators"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="active")
    user_sessions = db.relationship("UserSession", backref="moderator", lazy=True)

    def __repr__(self):
        return f"<Moderator {self.fullname}>"

    def to_dict(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "is_super_admin": self.is_super_admin,
            "status": self.status
        }

    @staticmethod
    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        return False


class UserSession(db.Model):
    __tablename__ = "user_sessions"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    mod_id = db.Column(db.String(50), db.ForeignKey("moderators.id"), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<UserSession {self.mod_id}>"


class Spouse(db.Model):
    __tablename__ = "spouse"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    husband_1 = db.Column(db.String(50), db.ForeignKey('member.id'))
    wife_2 = db.Column(db.String(50), db.ForeignKey('member.id'))
    other_spouses = db.relationship("OtherSpouse", backref="spouse", lazy=True)
    children = db.relationship("Child", backref="spouse", lazy=True)


class OtherSpouse(db.Model):
    __tablename__ = "other_spouse"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    member_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    member_related_to = db.Column(db.String(50), db.ForeignKey('member.id'))
    relationship_type = db.Column(SQLAlchemyEnum(RelationshipType))
    spouse_id = db.Column(db.String(50), db.ForeignKey('spouse.id'))


class Child(db.Model):
    __tablename__ = "child"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    member_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    spouse_id = db.Column(db.String(50), db.ForeignKey('spouse.id'))
    child_type = db.Column(SQLAlchemyEnum(ChildType))


def create_user(email, password):
    mod = Moderators(email=email, password=password)
    db.session.add(mod)
    db.session.commit()
    return mod


def verify_user_login(email, password):
    mod = Moderators.query.filter_by(email=email).first()
    if mod and hasher.verify(password, mod.password):
        return mod
    return False


def create_otp_token(mod_id, otp=None, token=None):
    if otp:
        user_session = UserSession.query.filter_by(mod_id=mod_id).first()
        if user_session:
            user_session.otp = otp
            user_session.otp_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(mod_id=mod_id, otp=otp,
                                       otp_expires_at=datetime.now() + timedelta(minutes=10))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    elif token:
        user_session = UserSession.query.filter_by(mod_id=mod_id).first()
        if user_session:
            user_session.token = token
            user_session.token_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            user_session = UserSession(mod_id=mod_id, token=token,
                                       token_expires_at=datetime.now() + timedelta(minutes=10))
            db.session.add(user_session)
            db.session.commit()
        return user_session
    return None


def get_mod_by_email(email):
    user = Moderators.query.filter_by(email=email.lower()).first()
    return user


def valid_email(email):
    return Moderators.validate_email(email)


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
def update_user(mod_id,  **kwargs):
    mod = Moderators.query.filter_by(id=mod_id).first()
    if not mod:
        return False
    
    # Update user attributes with provided keyword arguments
    mod.password = kwargs.get("password") or mod.password
    mod.email = kwargs.get("email") or mod.email
    mod.is_super_admin = kwargs.get("is_super_admin") or mod.is_super_admin
    # hash password
    mod.password = hasher.hash(mod.password)
    
    db.session.commit()
    return True


def get_family_chain(user_id):
    user = User.query.get(user_id)
    if not user:
        return None

    family = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'gender': user.gender.value,
        'status': user.status.value,
        'dob': user.dob.strftime("%d-%b-%Y") if user.dob else None,
        'parents': [],
        'partners': [],
        'children': []
    }

    # Get parents
    parent_relationships = Relationship.query.filter_by(partner_id=user.id).all()
    for relationship in parent_relationships:
        parent = User.query.get(relationship.person_id)
        if parent:
            family['parents'].append({
                'id': parent.id,
                'first_name': parent.first_name,
                'last_name': parent.last_name,
                'gender': parent.gender.value
            })

    # Get partners
    partner_relationships = Relationship.query.filter_by(person_id=user.id).all()
    for relationship in partner_relationships:
        partner = User.query.get(relationship.partner_id)
        if partner:
            family['partners'].append({
                'id': partner.id,
                'first_name': partner.first_name,
                'last_name': partner.last_name,
                'gender': partner.gender.value,
                'relationship_type': relationship.relationship_type.value
            })

    # Get children
    children_relationships = Child.query.filter_by(parent_id=user.id).all()
    for child_relationship in children_relationships:
        child = User.query.get(child_relationship.child_id)
        if child:
            family['children'].append(get_family_chain(child.id))  # Recursive call

    return family


def link_family_members(husband_id, wife_ids, child_ids):
    # Fetch the husband from the database
    husband = User.query.get(husband_id)

    if not husband:
        raise ValueError("Husband not found in the database.")

    # Establish Relationships with Wives
    for wife_id in wife_ids:
        wife = User.query.get(wife_id)
        if not wife:
            raise ValueError(f"Wife with ID {wife_id} not found in the database.")

        husband_wife_relationship = Relationship(
            person_id=husband.id,
            partner_id=wife.id,
            relationship_type=RelationshipType.husband
        )

        wife_husband_relationship = Relationship(
            person_id=wife.id,
            partner_id=husband.id,
            relationship_type=RelationshipType.wife
        )

        db.session.add(husband_wife_relationship)
        db.session.add(wife_husband_relationship)

    # Link Children
    for child_id in child_ids:
        child = User.query.get(child_id)
        if not child:
            raise ValueError(f"Child with ID {child_id} not found in the database.")

        # Establish Child Relationships
        child_relationship_husband = Child(
            parent_id=husband.id,
            child_id=child.id
        )

        child_relationship_wife = Child(
            parent_id=wife.id,
            child_id=child.id
        )

        db.session.add(child_relationship_husband)
        db.session.add(child_relationship_wife)

    # Commit all relationships to the database
    db.session.commit()
