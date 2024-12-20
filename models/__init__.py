from extensions import db
from enum import Enum
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.hybrid import hybrid_property
import re
import datetime
from utils import hex_uuid, extract_public_id
import pprint
from sqlalchemy.orm import configure_mappers, mapper, foreign

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
    mistress = "Mistress"


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
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    child = db.relationship(
        "Child",
        foreign_keys="[Child.member_id]",
        backref="member",
        overlaps="child_as_member",
        lazy=True,
        uselist=False,
        cascade="all, delete, delete-orphan",
    )
    child_owner = db.relationship(
        "Child",
        foreign_keys="[Child.mother_id]",
        backref="mother",
        overlaps="child",
        lazy=True,
        uselist=False,
        cascade="all, delete, delete-orphan",
    )
    # Relationships for spouses (as a husband and as a wife)
    husband_spouse = db.relationship(
        "Spouse",
        foreign_keys="[Spouse.husband_id]",
        backref="husband_member",
        overlaps="spouse_as_husband",
        cascade="all, delete, delete-orphan",
        lazy=True,
    )

    wife_spouse = db.relationship(
        "Spouse",
        foreign_keys="[Spouse.wife_id]",
        backref="wife_member",
        overlaps="spouse_as_wife",
        cascade="all, delete, delete-orphan",
        lazy=True,
    )

    other_spouses_as_member = db.relationship(
        "OtherSpouse",
        backref="member_as_primary",
        foreign_keys="[OtherSpouse.member_id]",
        lazy=True,
        overlaps="other_spouses_as_related",
        cascade="all, delete, delete-orphan",
    )
    other_spouses_as_related = db.relationship(
        "OtherSpouse",
        backref="member_as_related",
        foreign_keys="[OtherSpouse.member_related_to]",
        lazy=True,
        overlaps="other_spouses_as_member",
        cascade="all, delete, delete-orphan",
    )

    @hybrid_property
    def spouse(self):
        if self.spouse_as_husband:
            return self.spouse_as_husband[0].husband
        elif self.spouse_as_wife:
            print("spouse_as_wife")
            return self.spouse_as_wife[0].wife
        return None

    # check if husband id and wife id is in spouse table
    @hybrid_property
    def spouse_as_husband_and_wife(self):
        return self.husband_spouse and self.wife_spouse

    @hybrid_property
    def other_spouses(self):
        return self.other_spouses_as_member

    @hybrid_property
    def other_spouses2(self):
        return self.other_spouses_as_related

    def __init__(
        self,
        first_name,
        last_name,
        gender,
        img_str=None,
        phone_number=None,
        dob=None,
        status=None,
        deceased_at=None,
        occupation=None,
        birth_place=None,
        birth_name=None,
    ):
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
            "public_id": extract_public_id(self.img_str) if self.img_str else None,
            "phone_number": self.phone_number,
            "dob": self.dob.strftime("%Y-%m-%d") if self.dob else None,
            "user_status": self.status.value,
            "deceased_at": (
                self.deceased_at.strftime("%Y-%m-%d") if self.deceased_at else None
            ),
            "occupation": self.occupation,
            "birth_name": self.birth_name,
            "birth_place": self.birth_place,
            "story_line": self.story_line,
            "has_spouse": has_spouse(self.id, self.gender.value),
            "only_child": only_child_create(self),
        }
        return member_dict
        # return {key: value for key, value in member_dict.items() if value}

    def to_dict2(self):
        member_dict = {
            "id": self.id,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "gender": self.gender.value,
        }
        return member_dict

    def __repr__(self):
        return f"<Member {self.last_name}>"


class Gallery(db.Model):
    __tablename__ = "gallery"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    event_name = db.Column(db.String(50), nullable=True)
    image = db.Column(db.Text, nullable=True)
    event_year = db.Column(db.String(50), nullable=True)

    def __init__(self, event_name, image, event_year):
        self.event_name = event_name
        self.image = image
        self.event_year = event_year

    def to_dict(self):
        return {
            "id": self.id,
            "event_name": self.event_name,
            "image": self.image,
            "event_year": self.event_year,
        }


class Logo(db.Model):
    __tablename__ = "logo"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    logo_image = db.Column(db.Text, nullable=True)
    logo_title = db.Column(db.String(50), nullable=True)
    full_name = db.Column(db.String(50), nullable=True)
    hero_image = db.Column(db.Text, nullable=True)
    story_year = db.Column(db.Integer, nullable=True)
    ancestor_name = db.Column(db.String(50), nullable=True)
    hero_text = db.Column(db.Text, nullable=True)
    directory_image = db.Column(db.Text, nullable=True)
    clan_name = db.Column(db.String(50), nullable=True)

    def __init__(
        self,
        logo_image,
        logo_title,
        full_name,
        hero_image,
        story_year,
        ancestor_name,
        hero_text,
        directory_image,
        clan_name,
    ):
        self.logo_image = logo_image
        self.logo_title = logo_title
        self.full_name = full_name
        self.hero_image = hero_image
        self.story_year = story_year
        self.ancestor_name = ancestor_name
        self.hero_text = hero_text
        self.directory_image = directory_image
        self.clan_name = clan_name

    def to_dict(self):
        return {
            "id": self.id,
            "logo_image": self.logo_image,
            "logo_title": self.logo_title,
            "full_name": self.full_name,
            "hero_image": self.hero_image,
            "story_year": self.story_year,
            "ancestor_name": self.ancestor_name,
            "hero_text": self.hero_text,
            "directory_image": self.directory_image,
            "clan_name": self.clan_name,
        }


class Moderators(db.Model):
    __tablename__ = "moderators"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default="moderator")
    password = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="active")
    mod_sessions = db.relationship(
        "ModSession",
        backref="moderator",
        lazy=True,
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self):
        return f"<Moderator {self.fullname}>"

    def to_dict(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "is_super_admin": self.is_super_admin,
            "role": self.role,
            "status": self.status,
        }

    @staticmethod
    def validate_email(email):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
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
    husband_id = db.Column(db.String(50), db.ForeignKey("member.id"))
    wife_id = db.Column(db.String(50), db.ForeignKey("member.id"))
    other_spouses = db.relationship("OtherSpouse", backref="spouse", lazy=True)
    children = db.relationship("Child", backref="spouse", lazy=True)
    husband = db.relationship(
        "Member",
        foreign_keys=[husband_id],
        backref="spouse_as_husband",
        overlaps="husband_spouse,husband_member",
    )
    wife = db.relationship(
        "Member",
        foreign_keys=[wife_id],
        backref="spouse_as_wife",
        overlaps="wife_spouse,wife_member",
    )
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    date_updated = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def to_dict(self, member_id=None):
        return_dict = {
            "id": self.id,
            "husband": self.husband.to_dict() if self.husband else {},
            "wife": self.wife.to_dict() if self.wife else {},
        }
        if (
            member_id
            and self.other_spouses
            and member_id == self.other_spouses[0].member_related_to
        ):
            return_dict["other_spouses"] = [
                other_spouse.to_dict() for other_spouse in self.other_spouses
            ]
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
    member_id = db.Column(db.String(50), db.ForeignKey("member.id"))
    member_related_to = db.Column(db.String(50), db.ForeignKey("member.id"))
    relationship_type = db.Column(SQLAlchemyEnum(RelationshipType))
    spouse_id = db.Column(db.String(50), db.ForeignKey("spouse.id"))

    member = db.relationship(
        "Member",
        foreign_keys=[member_id],
        backref="primary_other_spouses",
        overlaps="member_as_primary,other_spouses_as_member",
    )
    related_member = db.relationship(
        "Member",
        foreign_keys=[member_related_to],
        backref="related_other_spouses",
        overlaps="member_as_related,other_spouses_as_related",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "relationship_type": self.relationship_type.value,
            "member": self.member.to_dict() if self.member else None,
            "related_member": (
                self.related_member.to_dict() if self.related_member else None
            ),
        }

    def to_dict2(self):
        return {
            **self.member.to_dict2(),
            "relationship_type": self.relationship_type.value,
        }


class Child(db.Model):
    __tablename__ = "child"
    id = db.Column(db.String(50), primary_key=True, default=hex_uuid)
    member_id = db.Column(db.String(50), db.ForeignKey("member.id"))
    spouse_id = db.Column(db.String(50), db.ForeignKey("spouse.id"))
    mother_id = db.Column(db.String(50), db.ForeignKey("member.id"), nullable=True)
    child_type = db.Column(SQLAlchemyEnum(ChildType))

    def to_dict(self):
        return self.member.to_dict()

    def to_dict2(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "spouse_id": self.spouse_id,
            "child_type": self.child_type.value,
        }


def create_mod(email, password, fullname, role, is_super_admin=False):
    mod = Moderators(
        email=email,
        password=hasher.hash(password),
        is_super_admin=is_super_admin,
        fullname=fullname,
        role=role,
    )
    db.session.add(mod)
    db.session.commit()
    return mod


def has_spouse(member_id, gender):
    print("member_id", member_id, "gender", gender)
    if gender == "Male":
        print("This is a male")
        # filter husband id
        spouse = Spouse.query.filter_by(husband_id=member_id).first()
        if not spouse:
            return False
        return True if spouse.wife_id else False
    elif gender == "Female":
        print("This is a female")
        # filter wife id
        spouse = Spouse.query.filter_by(wife_id=member_id).first()
        if not spouse:
            return False
        return True if spouse.husband_id else False
    return False


# get spouse details
def get_spouse_details(member_id):
    spouse = Spouse.query.filter(
        db.or_(Spouse.husband_id == member_id, Spouse.wife_id == member_id)
    ).first()
    if spouse:
        return spouse.to_dict(member_id), spouse
    return {}, spouse


def save_member(payload):
    if payload.get("dob") and not isinstance(payload.get("dob"), date):
        payload["dob"] = datetime.strptime(payload.get("dob"), "%Y-%m-%d").date()

    if payload.get("deceased_at") and not isinstance(payload.get("deceased_at"), date):
        payload["deceased_at"] = datetime.strptime(
            payload.get("deceased_at"), "%Y-%m-%d"
        ).date()
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
        birth_name=payload.get("birth_name"),
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
    res, err = save_spouse_details(
        husband_id, wife_id, data.get("other_spouses"), data.get("children")
    )
    return res, err


def save_spouse_details(husband_id, wife_id, other_spouses, children):
    print("husband_id", husband_id, "wife_id", wife_id)
    if other_spouses and not isinstance(other_spouses, list):
        return False, "other spouses must be an array"
    if children and not isinstance(children, list):
        return False, "children must be an array"
    # query for husband and wife
    spouse = Spouse.query.filter_by(husband_id=husband_id).first()
    if spouse:
        if spouse.wife_id:
            print("found Wife")
            return False, "already have wife"
        print("found Husband")
        # Update wife_id if spouse exists
        spouse.wife_id = wife_id
    else:
        print("not found husband")
        # Try to find a spouse by wife_id
        spouse = Spouse.query.filter_by(wife_id=wife_id).first()
        if spouse:
            if spouse.husband_id:
                return False, "already have husband"
            print("found wife")
            # Update husband_id if spouse exists
            spouse.husband_id = husband_id
        else:
            print("creating new spouse")
            # Create a new Spouse record if neither exists
            spouse = Spouse(husband_id=husband_id, wife_id=wife_id)
            db.session.add(spouse)

        # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        print(e, "error from save_spouse_details")
        db.session.rollback()
        return False
    if other_spouses:
        for other_spouse in other_spouses:
            member = save_member(other_spouse)
            if member.gender == Gender.female:
                member_related_to = husband_id or wife_id
            else:
                member_related_to = wife_id or husband_id
            save_other_spouses(
                member.id,
                member_related_to,
                other_spouse["relationship_type"],
                spouse.id,
            )
    if children:
        for child in children:
            child_member = save_member(child)
            save_child(
                child_member.id,
                spouse.id,
                child["child_type"],
                child.get("mother_id", None),
            )
    return spouse, None


def save_other_spouses(member_id, member_related_to, relationship_type, spouse_id):
    other_spouse = OtherSpouse(
        member_id=member_id,
        member_related_to=member_related_to,
        relationship_type=RelationshipType(relationship_type.title()),
        spouse_id=spouse_id,
    )
    db.session.add(other_spouse)
    db.session.commit()
    return other_spouse


def save_child(member_id, spouse_id, child_type, mother_id):
    child = Child(
        member_id=member_id,
        spouse_id=spouse_id,
        child_type=ChildType(child_type.title()),
        mother_id=mother_id,
    )
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
    pprint.pprint(payload)
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
        if member.gender == Gender.male:
            wife_id = sec_mem.id
            husband_id = member.id
            # print("this is female", wife_id, husband_id)
        else:
            wife_id = member.id
            husband_id = sec_mem.id
            # print("this is male", wife_id, husband_id)
        save_spouse_details(
            husband_id, wife_id, payload.get("other_spouses"), payload.get("children")
        )
    spouse = (
        Spouse.query.filter_by(husband_id=member.id).first()
        or Spouse.query.filter_by(wife_id=member.id).first()
    )
    if not payload.get("spouse") and payload.get("other_spouses"):
        for other_spouse in payload.get("other_spouses"):
            member = save_member(other_spouse)
            member_related_to = member_id
            save_other_spouses(
                member.id,
                member_related_to,
                other_spouse["relationship_type"],
                spouse.id,
            )
    if (
        not payload.get("spouse")
        and not payload.get("other_spouses")
        and payload.get("children")
    ):
        if member.other_spouses:
            spouse = get_spouse_related_to_other_spouse(
                member.other_spouses[0].member_related_to
            )
            for child in payload.get("children"):
                child_member = save_member(child)
                save_child(child_member.id, spouse.id, child["child_type"], member.id)
            return None
        if not spouse:
            return "This member has no spouse"
        for child in payload.get("children"):
            child_member = save_member(child)
            mother_id = None if child.get("mother_id") == "" else child["mother_id"]
            save_child(child_member.id, spouse.id, child["child_type"], mother_id)
    db.session.commit()
    return None


def get_spouse_related_to_other_spouse(member_related_to):
    spouse = Spouse.query.filter(
        (Spouse.husband_id == member_related_to) | (Spouse.wife_id == member_related_to)
    ).first()
    return spouse


def get_children(spouse_id, spouse_inst, member_id):
    children = Child.query.filter_by(spouse_id=spouse_id).all()
    if spouse_inst.wife_id == member_id:
        print("spouse is wife and member")
        all_children = [
            child.to_dict() for child in children if child.mother_id is None
        ]
    else:
        all_children = [child.to_dict() for child in children]
    return all_children


def get_children2(spouse_id):
    children = Child.query.filter_by(spouse_id=spouse_id).all()
    return children


def get_other_spouses(spouse_id):
    other_spouses = OtherSpouse.query.filter_by(member_related_to=spouse_id).all()
    all_other_spouses = [other_spouse.to_dict() for other_spouse in other_spouses]
    return all_other_spouses


def get_parents(spouse_id, child_mother_id):
    parents = Spouse.query.filter_by(id=spouse_id).first()
    if parents:
        if child_mother_id:
            mother = Member.query.filter_by(id=child_mother_id).first()
            return {"father": parents.husband.to_dict(), "mother": mother.to_dict()}
        return {"father": parents.husband.to_dict(), "mother": parents.wife.to_dict()}
    return None


def get_related_spouse(member_id, member_relate_id):
    spouse = OtherSpouse.query.filter_by(
        member_related_to=member_relate_id, member_id=member_id
    ).first()
    if spouse:
        return (
            {
                "husband": spouse.related_member.to_dict(),
                "wife": spouse.member.to_dict(),
            }
            if spouse.member.gender == Gender.female
            else {
                "husband": spouse.member.to_dict(),
                "wife": spouse.related_member.to_dict(),
            }
        )
    return {}


def only_child_create(member):
    if member.other_spouses:
        return True
    if member.spouse and member.gender == Gender.female:
        return True
    return False


def get_family_chain(member_id):
    member = Member.query.filter_by(id=member_id).first()
    if not member:
        return None
    family_chain = {}
    # check if member has parents/ he's a child
    if member.child:
        parent = get_parents(member.child.spouse_id, member.child.mother_id)
        family_chain["parents"] = parent
        family_chain["child"] = member.to_dict()

    # get spouse details
    if member.spouse:
        print("gotten")
        spouse, spouse_inst = get_spouse_details(member_id)
        children = get_children(spouse["id"], spouse_inst, member_id)
        family_chain["spouse"] = spouse
        family_chain["children"] = children

        # remove the child key
        if "child" in family_chain:
            del family_chain["child"]

    if member.other_spouses:
        spouse = get_related_spouse(
            member_id, member.other_spouses[0].member_related_to
        )
        family_chain["spouse"] = spouse
        family_chain["children"] = get_other_spouse_children(member_id)

    return family_chain


def get_other_spouse_children(member_id):
    other_spouse_children = Child.query.filter_by(mother_id=member_id).all()
    return [child.to_dict() for child in other_spouse_children]


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
            mod_session = ModSession(
                mod_id=mod_id,
                otp=otp,
                otp_expires_at=datetime.now() + timedelta(minutes=10),
            )
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
            mod_session = ModSession(
                mod_id=mod_id,
                token=token,
                token_expires_at=datetime.now() + timedelta(minutes=10),
            )
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
                Member.last_name.ilike(f"%{fullname}%"),
            )
        )
    members = members.order_by(Member.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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
    mod.role = kwargs.get("role") or mod.role
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
        mods = mods.filter(Moderators.fullname.ilike(f"%{fullname}%"))

    if email:
        mods = mods.filter(Moderators.email.ilike(f"%{email}%"))

    mods = mods.order_by(Moderators.fullname.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return mods


def get_members_other_spouses(member_id):
    others = OtherSpouse.query.filter_by(member_related_to=member_id).all()
    return [other.to_dict2() for other in others]


# Add images, event_year, event_name
def items_to_gallery(fam_image, fam_event_name, fam_event_year):
    try:
        gall = Gallery(
            image=fam_image, event_name=fam_event_name, event_year=fam_event_year
        )
        db.session.add(gall)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()  # Rollback on error
        print(f"Error adding to gallery: {e}")
        return False


# Get items from gallery
def get_items_from_gallery():
    try:
        items = Gallery.query.all()
        print("Getting items from gallery", items)
        return items
    except Exception as e:
        print(f"Error getting items from gallery: {e}")
        return None


# Delete gallery item


def delete_gallery_item(gallery_id):
    try:
        item = Gallery.query.filter_by(id=gallery_id).first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()  # Rollback on error
        print(f"Error deleting gallery item: {e}")
        return False


def get_one_fam_member(member_id, delete=False):
    member = Member.query.filter_by(id=member_id).first()
    if delete:
        return member
    return member.to_dict() if member else None


# Function to add or update logo items
def add_or_update_logo(
    logo_image,
    logo_title,
    full_name,
    hero_image,
    story_year,
    ancestor_name,
    hero_text,
    directory_image,
    clan_name,
):
    try:
        existing_logo = Logo.query.first()

        if existing_logo:
            existing_logo.logo_image = (
                logo_image if logo_image else existing_logo.logo_image
            )
            existing_logo.logo_title = (
                logo_title if logo_title else existing_logo.logo_title
            )
            existing_logo.full_name = (
                full_name if full_name else existing_logo.full_name
            )
            existing_logo.hero_image = (
                hero_image if hero_image else existing_logo.hero_image
            )
            existing_logo.story_year = (
                story_year if story_year else existing_logo.story_year
            )
            existing_logo.ancestor_name = (
                ancestor_name if ancestor_name else existing_logo.ancestor_name
            )
            existing_logo.hero_text = (
                hero_text if hero_text else existing_logo.hero_text
            )
            existing_logo.directory_image = (
                directory_image if directory_image else existing_logo.directory_image
            )
            existing_logo.clan_name = (
                clan_name if clan_name else existing_logo.clan_name
            )
        else:
            existing_logo = Logo(
                logo_image=logo_image,
                logo_title=logo_title,
                full_name=full_name,
                hero_image=hero_image,
                story_year=story_year,
                ancestor_name=ancestor_name,
                hero_text=hero_text,
                directory_image=directory_image,
                clan_name=clan_name,
            )
            db.session.add(existing_logo)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding/updating logo: {e}")
        return False


def get_logo_details():
    logo = Logo.query.first()
    return logo.to_dict()


# def recursive_delete(member, visited=None):
#     if visited is None:
#         visited = set()
#
#     # If the member has already been visited, return to avoid infinite recursion
#     if member.id in visited:
#         return
#
#     # Mark the member as visited
#     visited.add(member.id)
#
#     # If the member is a husband, recursively delete the wife and associated records
#     if member.husband_spouse:
#         for spouse in member.husband_spouse:
#             print(spouse.wife_id, "the wife id")
#             wife_member = Member.query.get(spouse.wife_id)
#             print(wife_member, "the wife member")
#             if wife_member:
#                 children = get_children2(spouse.id)  # Use the get_children function to fetch children
#
#                 for child in children:
#                     child_member = child.member
#                     print(child_member, "child_member")
#                     if child_member:
#                         db.session.delete(child)
#                         db.session.delete(child_member)
#                         db.session.commit()
#                         recursive_delete(child_member, visited)
#                 db.session.delete(wife_member)
#                 # recursive_delete(wife_member, visited)  # Recursively delete the wife and her records
#             db.session.delete(spouse)  # Delete the spouse record where the member is the husband
#
#     # If the member is a wife, recursively delete the husband and associated records
#     if member.wife_spouse:
#         for spouse in member.wife_spouse:
#             husband_member = Member.query.get(spouse.husband_id)
#             print(husband_member, "husband_member")
#             if husband_member:
#                 children = get_children2(spouse.id)  # Use the get_children function to fetch children
#
#                 for child in children:
#                     child_member = child.member
#                     print(child_member, "child_member")
#                     if child_member:
#                         db.session.delete(child)
#                         db.session.delete(child_member)
#                         db.session.commit()
#                         recursive_delete(child_member, visited)
#                 db.session.delete(husband_member)
#                 # recursive_delete(husband_member, visited)  # Recursively delete the husband and his records
#             db.session.delete(spouse)  # Delete the spouse record where the member is the wife
#
#     # Recursively delete other spouses linked to the member
#     if member.other_spouses2:
#         print("yes it exist", member.other_spouses2)
#         for other_spouse in member.other_spouses2:
#             # Use member_id to get the related member (primary member in the relationship)
#             spouse_member = Member.query.filter_by(id=other_spouse.member_id).first()
#             print(spouse_member, "other spouse_member")
#             if spouse_member:
#                 db.session.delete(spouse_member)
#                 recursive_delete(spouse_member, visited)  # Recursively delete the member linked as the other spouse
#             db.session.delete(other_spouse)  # Delete the other_spouse record
#
#     # Finally, delete the member
#     db.session.delete(member)
#
#     # Commit changes to the database after all related records are deleted
#     db.session.commit()
#     print("deleted")
#
#     return True


def recursive_delete(member, visited=None):
    if visited is None:
        visited = set()

    # If the member has already been visited, return to avoid infinite recursion
    if member.id in visited:
        return

    # Mark the member as visited
    visited.add(member.id)

    # Function to handle spouse and child deletion logic
    def delete_spouse_and_children(spouse_id, spouse_type):
        spouse_member = Member.query.get(spouse_id)
        if spouse_member:
            children = get_children2(
                spouse_type.id
            )  # Get the children linked to the spouse
            for child in children:
                child_member = child.member
                if child_member:
                    db.session.delete(child)  # Delete the child record
                    db.session.delete(child_member)  # Delete the child member
                    recursive_delete(child_member, visited)
            db.session.delete(spouse_member)  # Delete the spouse member

    # Process husband-spouse relationships
    if member.husband_spouse:
        for spouse in member.husband_spouse:
            delete_spouse_and_children(spouse.wife_id, spouse)
            db.session.delete(spouse)  # Delete the spouse record

    # Process wife-spouse relationships
    if member.wife_spouse:
        for spouse in member.wife_spouse:
            delete_spouse_and_children(spouse.husband_id, spouse)
            db.session.delete(spouse)  # Delete the spouse record

    # Process other spouses (other_spouses2)
    if member.other_spouses2:
        for other_spouse in member.other_spouses2:
            spouse_member = Member.query.get(other_spouse.member_id)
            if spouse_member:
                db.session.delete(spouse_member)
                recursive_delete(spouse_member, visited)
            db.session.delete(other_spouse)  # Delete the other spouse record

    # Delete the main member and commit changes in one transaction
    db.session.delete(member)
    db.session.commit()

    return True


"""
    def recursive_delete(member):
        # Delete all children of this member
        for child in member.children:
            # Recursively delete the child's spouse and their children
            for grandchild in child.children:
                recursive_delete(grandchild)  # Recursively delete grandchildren
            # Delete the child's spouse
            spouses = Spouse.query.filter(
                (Spouse.husband_id == child.id) | (Spouse.wife_id == child.id)
            ).all()
            for spouse in spouses:
                spouse_member_id = spouse.wife_id if spouse.husband_id == child.id else spouse.husband_id
                spouse_member = Member.query.get(spouse_member_id)
                if spouse_member:
                    # Recursively delete other spouses
                    for other_spouse in spouse_member.primary_other_spouses:
                        db.session.delete(other_spouse)
                    for other_spouse in spouse_member.related_other_spouses:
                        db.session.delete(other_spouse)
                    db.session.delete(spouse_member)

            # Delete the child as a Member
            db.session.delete(child)

        # Now delete the member itself
        db.session.delete(member)

    # Call the recursive delete function
    recursive_delete(member)

    # Commit the changes
    db.session.commit()
"""
