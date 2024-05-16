# so_well/models.py
from . import db
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database, TSVectorType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Numeric, Date, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.sql import func


# Creating the Database if it does not exist (ensure your DB URI includes correct creds)
if not database_exists(db.engine.url):
    create_database(db.engine.url)

def generate_uuid():
    return str(uuid.uuid4())


# Entities Schema Models
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'security'}
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())

class Voter(db.Model):
    __tablename__ = 'voters'
    __table_args__ = {'schema': 'voters'}

    identification_number = db.Column(db.String(50), primary_key=True)
    last_name = db.Column(db.String(50), index=True)
    first_name = db.Column(db.String(50), index=True)
    middle_name = db.Column(db.String(50))
    suffix = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    dob = db.Column(db.String(10))
    registration_date = db.Column(db.String(10))
    effective_date = db.Column(db.String(10))
    status = db.Column(db.String(255))


    # Foreign keys to other tables
    residence_address_id = db.Column(db.Integer, db.ForeignKey('voters.address.id'))
    mailing_address_id = db.Column(db.Integer, db.ForeignKey('voters.address.id'))
    locality_id = db.Column(db.Integer, db.ForeignKey('voters.locality.id'))

    full_name_searchable = db.Column(TSVectorType('first_name', 'last_name', 'middle_name', 'suffix'))

    residence_address = relationship("Address", foreign_keys=[residence_address_id])
    mailing_address = relationship("Address", foreign_keys=[mailing_address_id])
    locality = relationship("Locality")

    def __repr__(self):
        return f"<Voter(Identification number='{self.identification_number}', Name='{self.first_name} {self.last_name}')>"

class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = {'schema': 'voters'}

    id = db.Column(db.Integer, primary_key=True)
    house_number = db.Column(db.String(50))
    house_number_suffix = db.Column(db.String(3))
    street_name = db.Column(db.String(50), index=True)
    street_type = db.Column(db.String(100))
    direction = db.Column(db.String(50))
    post_direction = db.Column(db.String(50))
    apt_num = db.Column(db.String(50))
    city = db.Column(db.String(50), index=True)
    state = db.Column(db.String(50))
    zip = db.Column(db.String(10), index=True)

    full_address_searchable = db.Column(TSVectorType('house_number', 'street_name', 'street_type', 'city', 'zip'))

    def __repr__(self):
        return f"<Address(City='{self.city}', Street='{self.street_name}', House='{self.house_number}', Apt='{self.apt_num}')>"

class Locality(db.Model):
    __tablename__ = 'locality'
    __table_args__ = {'schema': 'voters'}

    id = db.Column(db.Integer, primary_key=True)
    locality_code = db.Column(db.String(3))
    locality_name = db.Column(db.String(255))
    precinct_code = db.Column(db.String(255))
    precinct_name = db.Column(db.String(255))
    town_code = db.Column(db.String(255))
    town_name = db.Column(db.String(255))
    town_prec_code = db.Column(db.String(255))
    town_prec_name = db.Column(db.String(255))
    congressional_district = db.Column(db.String(255))
    state_senate_district = db.Column(db.String(255))
    house_delegates_district = db.Column(db.String(255))
    super_district_code = db.Column(db.String(255))
    super_district_name = db.Column(db.String(255))

    voters = relationship('Voter', back_populates='locality')

    def __repr__(self):
        return f"<Locality(Name='{self.locality_name}', Precinct='{self.precinct_name}')>"
