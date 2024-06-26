# so_well/models.py
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database, TSVectorType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, func, Text
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid

db = SQLAlchemy()
migrate = Migrate()

def generate_uuid():
    return str(uuid.uuid4())

# Models

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'security'}
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid, comment="Unique user ID")
    email = db.Column(db.String(255), unique=True, nullable=False, comment="User's email address")
    is_active = db.Column(db.Boolean, default=True, comment="Is the user active?")
    last_login = db.Column(db.DateTime, nullable=True, comment="Last login time")
    created_at = db.Column(db.DateTime, default=func.now(), comment="Record creation date")
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), comment="Record last update date")

class Voter(db.Model):
    __tablename__ = 'voters'
    __table_args__ = {'schema': 'electorate'}
    identification_number = db.Column(db.String(50), primary_key=True, comment="Voter's unique identification number")
    last_name = db.Column(db.String(50), index=True, nullable=False, comment="Voter's last name")
    first_name = db.Column(db.String(50), index=True, nullable=False, comment="Voter's first name")
    middle_name = db.Column(db.String(50), nullable=True, comment="Voter's middle name")
    suffix = db.Column(db.String(50), nullable=True, comment="Voter's name suffix")
    gender = db.Column(db.String(1), nullable=True, comment="Voter's gender")
    dob = db.Column(db.Date, nullable=True, comment="Voter's date of birth")
    registration_date = db.Column(db.Date, nullable=True, comment="Voter's registration date")
    effective_date = db.Column(db.Date, nullable=True, comment="Voter's effective date for the precinct")
    status = db.Column(db.String(255), nullable=True, comment="Voter's registration status")
    residence_address_id = db.Column(db.Integer, db.ForeignKey('electorate.address.id'), nullable=False, comment="Foreign key to residence address")
    mailing_address_id = db.Column(db.Integer, db.ForeignKey('electorate.address.id'), nullable=True, comment="Foreign key to mailing address")
    locality_id = db.Column(db.Integer, db.ForeignKey('electorate.locality.id'), nullable=False, comment="Foreign key to locality")
    full_name_searchable = db.Column(TSVectorType('first_name', 'last_name', 'middle_name', 'suffix'))
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False, comment="Record creation date")
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update date")
    residence_address = relationship("Address", foreign_keys=[residence_address_id])
    mailing_address = relationship("Address", foreign_keys=[mailing_address_id])
    locality = relationship("Locality", back_populates="voters")
    def __repr__(self):
        return f"<Voter(Identification number='{self.identification_number}', Name='{self.first_name} {self.last_name} {self.suffix}')>"

class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = {'schema': 'electorate'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Auto incrementing primary key")
    house_number = db.Column(db.String(50), nullable=False, comment="House number of residence")
    house_number_suffix = db.Column(db.String(3), nullable=True, comment="House number suffix")
    street_name = db.Column(db.String(50), index=True, nullable=False, comment="Street name of residence")
    street_type = db.Column(db.String(100), nullable=True, comment="Street type (e.g., Ave, Blvd)")
    direction = db.Column(db.String(50), nullable=True, comment="Street prefix direction (e.g., N, S)")
    post_direction = db.Column(db.String(50), nullable=True, comment="Street suffix direction")
    apt_num = db.Column(db.String(50), nullable=True, comment="Apartment number")
    city = db.Column(db.String(50), index=True, nullable=False, comment="City of residence")
    state = db.Column(db.String(50), nullable=False, comment="State of residence")
    zip = db.Column(db.String(10), index=True, nullable=False, comment="ZIP code of residence")
    full_address_searchable = db.Column(TSVectorType('house_number', 'street_name', 'street_type', 'city', 'zip'))
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False, comment="Record creation date")
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update date")
    def __repr__(self):
        return f"<Address(City='{self.city}', Street='{self.street_name}', House='{self.house_number}', Apt='{self.apt_num}')>"

class Locality(db.Model):
    __tablename__ = 'locality'
    __table_args__ = {'schema': 'electorate'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Auto incrementing primary key")
    locality_code = db.Column(db.String(3), nullable=False, comment="Locality FIPS code")
    locality_name = db.Column(db.String(255), nullable=False, comment="Name of locality")
    precinct_code = db.Column(db.String(255), nullable=True, comment="Code number for precinct")
    precinct_name = db.Column(db.String(255), nullable=True, comment="Name of precinct")
    town_code = db.Column(db.String(255), nullable=True, comment="Code number for town")
    town_name = db.Column(db.String(255), nullable=True, comment="Name of town")
    town_prec_code = db.Column(db.String(255), nullable=True, comment="Code number for town precinct")
    town_prec_name = db.Column(db.String(255), nullable=True, comment="Name of town precinct")
    congressional_district = db.Column(db.String(255), nullable=True, comment="Congressional District")
    state_senate_district = db.Column(db.String(255), nullable=True, comment="State Senate District")
    house_delegates_district = db.Column(db.String(255), nullable=True, comment="House of Delegates District")
    super_district_code = db.Column(db.String(255), nullable=True, comment="Super District code")
    super_district_name = db.Column(db.String(255), nullable=True, comment="Super District name")
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False, comment="Record creation date")
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update date")
    voters = relationship('Voter', back_populates='locality')
    def __repr__(self):
        return f"<Locality(Name='{self.locality_name}', Precinct='{self.precinct_name}')>"
