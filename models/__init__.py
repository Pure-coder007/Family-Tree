from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.hybrid import hybrid_property
import re
import datetime
from utils import hex_uuid
# from datetime import datetime
from datetime import datetime, timedelta, date


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
    story_line = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    child = db.relationship("Child", backref="member", lazy=True, uselist=False)
    # Relationships for spouses (as a husband and as a wife)
    husband_spouse = db.relationship("Spouse", foreign_keys="[Spouse.husband_id]", backref="husband_member",
                                     overlaps="spouse_as_husband")

    wife_spouse = db.relationship("Spouse", foreign_keys="[Spouse.wife_id]", backref="wife_member",
                                  overlaps="spouse_as_wife")

    other_spouses_as_member = db.relationship(
        "OtherSpouse",
        backref="member_as_primary",
        foreign_keys="[OtherSpouse.member_id]",
        lazy=True,
        overlaps="other_spouses_as_related"
    )
    other_spouses_as_related = db.relationship(
        "OtherSpouse",
        backref="member_as_related",
        foreign_keys="[OtherSpouse.member_related_to]",
        lazy=True,
        overlaps="other_spouses_as_member"
    )

    @hybrid_property
    def spouse(self):
        if self.spouse_as_husband:
            return self.spouse_as_husband[0].husband
        elif self.spouse_as_wife:
            print("spouse_as_wife")
            return self.spouse_as_wife[0].wife
        return None

    @hybrid_property
    def other_spouses(self):
        return self.other_spouses_as_member

    def __init__(self, first_name,
                 last_name, gender, img_str=None,
                 phone_number=None, dob=None, status=None, deceased_at=None,
                 occupation=None,
                 birth_place=None, birth_name=None):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.gender = Gender(gender.title())
        self.img_str = img_str
        self.phone_number = phone_number
        self.dob = dob
        self.status = Status(status) if status else Status.alive
        self.deceased_at = deceased_at or None
        self.occupation = occupation
        self.birth_name = birth_name
        self.birth_place = birth_place

    def to_dict(self):
        member_dict = {
            "id": self.id,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "gender": self.gender.value,
            "img_str": self.img_str,
            "phone_number": self.phone_number,
            "dob": self.dob.strftime("%d-%b-%Y") if self.dob else None,
            "user_status": self.status.value,
            "deceased_at": self.deceased_at.strftime("%d-%b-%Y") if self.deceased_at else None,
            "occupation": self.occupation,
            "birth_name": self.birth_name,
            "birth_place": self.birth_place,
            "story_line": self.story_line
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
    mod_sessions = db.relationship("ModSession", backref="moderator", lazy=True)

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


class ModSession(db.Model):
    __tablename__ = "mod_sessions"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    mod_id = db.Column(db.String(50), db.ForeignKey("moderators.id"), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<ModSession {self.mod_id}>"


class Spouse(db.Model):
    __tablename__ = "spouse"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    husband_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    wife_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    other_spouses = db.relationship("OtherSpouse", backref="spouse", lazy=True)
    children = db.relationship("Child", backref="spouse", lazy=True)
    husband = db.relationship("Member", foreign_keys=[husband_id], backref="spouse_as_husband",
                              overlaps="husband_spouse,husband_member")
    wife = db.relationship("Member", foreign_keys=[wife_id], backref="spouse_as_wife",
                           overlaps="wife_spouse,wife_member")
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    date_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def to_dict(self):
        return_dict = {
            "id": self.id,
            "husband": self.husband.to_dict() if self.husband else {},
            "wife": self.wife.to_dict() if self.wife else {},
            "other_spouses": [other_spouse.to_dict() for other_spouse in self.other_spouses]
            if self.other_spouses else [],
        }
        return {key: value for key, value in return_dict.items() if value}

    def parent_to_dict(self):
        return_dict = {
            "id": self.id,
            "father": self.husband.to_dict(),
            "mother": self.wife.to_dict(),
            # "other_spouses": [other_spouse.to_dict() for other_spouse in self.other_spouses],
            # "children": [child.to_dict() for child in self.children]
        }
        return {key: value for key, value in return_dict.items() if value}


class OtherSpouse(db.Model):
    __tablename__ = "other_spouse"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    member_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    member_related_to = db.Column(db.String(50), db.ForeignKey('member.id'))
    relationship_type = db.Column(SQLAlchemyEnum(RelationshipType))
    spouse_id = db.Column(db.String(50), db.ForeignKey('spouse.id'))

    member = db.relationship(
        "Member",
        foreign_keys=[member_id],
        backref="primary_other_spouses",
        overlaps="member_as_primary,other_spouses_as_member"
    )
    related_member = db.relationship(
        "Member",
        foreign_keys=[member_related_to],
        backref="related_other_spouses",
        overlaps="member_as_related,other_spouses_as_related"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "relationship_type": self.relationship_type.value,
            "member": self.member.to_dict() if self.member else None,
            "related_member": self.related_member.to_dict() if self.related_member else None
        }


class Child(db.Model):
    __tablename__ = "child"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    member_id = db.Column(db.String(50), db.ForeignKey('member.id'))
    spouse_id = db.Column(db.String(50), db.ForeignKey('spouse.id'))
    child_type = db.Column(SQLAlchemyEnum(ChildType))

    def to_dict(self):
        return self.member.to_dict()


def create_mod(email, password, fullname, is_super_admin=False):
    mod = Moderators(email=email, password=hasher.hash(password), is_super_admin=is_super_admin,
                      fullname=fullname)
    db.session.add(mod)
    db.session.commit()
    return mod


# get spouse details
def get_spouse_details(member_id):
    spouse = Spouse.query.filter(
        db.or_(Spouse.husband_id == member_id, Spouse.wife_id == member_id)
    ).first()
    if spouse:
        return spouse.to_dict()
    return {}


def save_member(payload):
    if payload.get("dob") and not isinstance(payload.get("dob"), date):
        payload["dob"] = datetime.strptime(payload.get("dob"), "%d-%m-%Y").date()

    if payload.get("deceased_at") and not isinstance(payload.get("deceased_at"), date):
        payload["deceased_at"] = datetime.strptime(payload.get("deceased_at"), "%d-%m-%Y").date()
    member = Member(
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        gender=payload.get("gender"),
        dob=payload.get("dob"),
        status=payload.get("status"),
        deceased_at=payload.get("deceased_at"),
        img_str=payload.get("img_str"),
        phone_number=payload.get("phone_number"),
        occupation=payload.get("occupation"),
        birth_place=payload.get("birth_place"),
        birth_name=payload.get("birth_name")
    )

    db.session.add(member)
    db.session.commit()
    return member


def create_member_with_spouse(data):
    member = save_member(data)
    print(member.gender == Gender.male, "this is gender")
    if member.gender == Gender.female:
        print("this is female")
        wife_id = member.id
        husband_id = None
    else:
        print("this is male")
        print(member.id, "the id for male")
        wife_id = None
        husband_id = member.id
    if data.get("spouse"):
        sec_mem = save_member(data.get("spouse"))
        if sec_mem.gender == Gender.female:
            wife_id = sec_mem.id
            husband_id = member.id
        else:
            wife_id = member.id
            husband_id = sec_mem.id

    print(husband_id, "the husband id")
    print(wife_id, "the wife id")
    res, err = save_spouse_details(husband_id, wife_id, data.get("other_spouses"), data.get("children"))
    return res, err


def save_spouse_details(husband_id, wife_id, other_spouses, children):
    if other_spouses and not isinstance(other_spouses, list):
        return False, "other spouses must be an array"
    if children and not isinstance(children, list):
        return False, "children must be an array"
    # query for husband and wife
    spouse = Spouse.query.filter_by(husband_id=husband_id).first()
    if not spouse:
        spouse = Spouse.query.filter_by(wife_id=wife_id).first()
    if spouse:
        spouse.wife_id = wife_id
    else:
        spouse = Spouse(husband_id=husband_id, wife_id=wife_id)
        db.session.add(spouse)
    db.session.commit()
    if other_spouses:
        for other_spouse in other_spouses:
            member = save_member(other_spouse)
            if member.gender == Gender.female:
                member_related_to = husband_id or wife_id
            else:
                member_related_to = wife_id or husband_id
            save_other_spouses(member.id, member_related_to,
                               other_spouse["relationship_type"], spouse.id)
    if children:
        for child in children:
            child_member = save_member(child)
            save_child(child_member.id, spouse.id, child["child_type"])
    return spouse, None


def save_other_spouses(member_id, member_related_to, relationship_type, spouse_id):
    other_spouse = OtherSpouse(member_id=member_id, member_related_to=member_related_to,
                               relationship_type=RelationshipType(relationship_type.title()), spouse_id=spouse_id)
    db.session.add(other_spouse)
    db.session.commit()
    return other_spouse


def save_child(member_id, spouse_id, child_type):
    child = Child(member_id=member_id, spouse_id=spouse_id, child_type=ChildType(child_type.title()))
    db.session.add(child)
    db.session.commit()
    return child


def edit_child(child_id, payload, remove=False):
    child = Child.query.filter_by(id=child_id).first()
    if not child:
        return False
    if remove:
        db.session.delete(child)
    else:
        child.spouse_id = payload.get("spouse_id") or child.spouse_id
        child.member_id = payload.get("member_id") or child.member_id
        child.child_type = payload.get("child_type") or child.child_type
    db.session.commit()
    return child


# update member
def edit_member(member_id, payload):
    member = Member.query.filter_by(id=member_id).first()
    if not member:
        return False
    member.first_name = payload.get("first_name") or member.first_name
    member.last_name = payload.get("last_name") or member.last_name
    member.dob = payload.get("dob") or member.dob
    member.status = payload.get("status") or member.status
    member.deceased_at = payload.get("deceased_at") or member.deceased_at
    member.img_str = payload.get("img_str") or member.img_str
    member.phone_number = payload.get("phone_number") or member.phone_number
    member.occupation = payload.get("occupation") or member.occupation
    member.birth_place = payload.get("birth_place") or member.birth_place
    member.birth_name = payload.get("birth_name") or member.birth_name
    member.gender = payload.get("gender") or member.gender
    member.story_line = payload.get("story_line") or member.story_line

    if payload.get("spouse"):
        sec_mem = save_member(payload.get("spouse"))
        if member.gender == Gender.female:
            wife_id = sec_mem.id
            husband_id = member.id
        else:
            wife_id = member.id
            husband_id = sec_mem.id
        save_spouse_details(husband_id, wife_id, payload.get("other_spouses"), payload.get("children"))
    db.session.commit()
    return member


def get_children(spouse_id):
    children = Child.query.filter_by(spouse_id=spouse_id).all()
    all_children = [child.to_dict() for child in children]
    return all_children


def get_other_spouses(spouse_id):
    other_spouses = OtherSpouse.query.filter_by(member_related_to=spouse_id).all()
    all_other_spouses = [other_spouse.to_dict() for other_spouse in other_spouses]
    return all_other_spouses


def get_parents(spouse_id):
    parents = Spouse.query.filter_by(id=spouse_id).first()
    if parents:
        return {
            "father": parents.husband.to_dict(),
            "mother": parents.wife.to_dict()
        }
    return None


def get_related_spouse(member_id, member_relate_id):
    spouse = OtherSpouse.query.filter_by(member_related_to=member_relate_id,
                                         member_id=member_id).first()
    if spouse:
        return {
            "husband": spouse.related_member.to_dict(),
            "wife": spouse.member.to_dict()
        } if spouse.member.gender == Gender.female else {
            "husband": spouse.member.to_dict(),
            "wife": spouse.related_member.to_dict()
        }
    return {}


def get_family_chain(member_id):
    member = Member.query.filter_by(id=member_id).first()
    if not member:
        return None
    family_chain = {}
    # check if member has parents/ he's a child
    if member.child:
        parent = get_parents(member.child.spouse_id)
        family_chain["parents"] = parent

    # get spouse details
    if member.spouse:
        print("gotten")
        spouse = get_spouse_details(member_id)
        children = get_children(spouse["id"])
        family_chain["spouse"] = spouse
        family_chain["children"] = children

    if member.other_spouses:
        spouse = get_related_spouse(member_id, member.other_spouses[0].member_related_to)
        family_chain["spouse"] = spouse

    return family_chain


def verify_mod_login(email, password):
    mod = Moderators.query.filter_by(email=email).first()
    if mod and hasher.verify(password, mod.password):
        return mod
    return False


def create_otp_token(mod_id, otp=None, token=None):
    if otp:
        mod_session = ModSession.query.filter_by(mod_id=mod_id).first()
        if mod_session:
            mod_session.otp = otp
            mod_session.otp_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            mod_session = ModSession(mod_id=mod_id, otp=otp,
                                       otp_expires_at=datetime.now() + timedelta(minutes=10))
            db.session.add(mod_session)
            db.session.commit()
        return mod_session
    elif token:
        mod_session = ModSession.query.filter_by(mod_id=mod_id).first()
        if mod_session:
            mod_session.token = token
            mod_session.token_expires_at = datetime.now() + timedelta(minutes=10)
            db.session.commit()
        else:
            mod_session = ModSession(mod_id=mod_id, token=token,
                                       token_expires_at=datetime.now() + timedelta(minutes=10))
            db.session.add(mod_session)
            db.session.commit()
        return mod_session
    return None


def get_mod_by_email(email):
    mod = Moderators.query.filter_by(email=email.lower()).first()
    return mod


def valid_email(email):
    return Moderators.validate_email(email)


def email_exists(email):
    return Moderators.query.filter_by(email=email.lower()).first()


def get_all_members(page, per_page, fullname):
    members = Member.query
    if fullname:
        members = members.filter(
            db.or_(
                Member.first_name.ilike(f"%{fullname}%"),
                Member.last_name.ilike(f"%{fullname}%")
            )
        )
    members = members.order_by(Member.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return members


# Update mod
def update_mod(mod_id, delete=False, **kwargs):
    mod = Moderators.query.filter_by(id=mod_id).first()
    if not mod:
        return False

    if delete:
        db.session.delete(mod)
        db.session.commit()
        return True

    # Update mod attributes with provided keyword arguments
    mod.email = kwargs.get("email") or mod.email
    mod.is_super_admin = kwargs.get("is_super_admin") or mod.is_super_admin
    mod.status = kwargs.get("status") or mod.status
    mod.fullname = kwargs.get("fullname") or mod.fullname
    # hash password

    db.session.commit()
    return True


# Change password
def change_password(mod_id, old_password, new_password):
    mod = Moderators.query.filter_by(id=mod_id).first()
    if not mod or not hasher.verify(old_password, mod.password):
        return False  

    mod.password = hasher.hash(new_password)
    db.session.commit()
    return True


# get all mods
def get_all_mods(page, per_page, fullname, email):
    mods = Moderators.query
    if fullname:
        mods = mods.filter(
            Moderators.fullname.ilike(f"%{fullname}%")
        )

    if email:
        mods = mods.filter(
            Moderators.email.ilike(f"%{email}%")
        )

    mods = mods.order_by(Moderators.fullname.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return mods


def get_one_fam_member(member_id):
    member = Member.query.filter_by(id=member_id).first()
    return member.to_dict()
