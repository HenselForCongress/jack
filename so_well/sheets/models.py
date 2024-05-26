# so_well/sheets/__init__.py
from sqlalchemy.orm import relationship, backref
from ..models import db, func

class Sheet(db.Model):
    __tablename__ = 'sheets'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey('signatures.circulators.id'), nullable=True)
    notary_id = db.Column(db.Integer, db.ForeignKey('signatures.notaries.id'), nullable=True)
    status = db.Column(db.String(50), db.ForeignKey('meta.sheet_status.status'), nullable=False, default='Printed')
    batch_id = db.Column(db.Integer, nullable=True)  # Updated later
    notarized_on = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    collector = relationship('Circulator', backref=backref('sheets', lazy=True))
    notary = relationship('Notary', backref=backref('sheets', lazy=True))

class SheetStatus(db.Model):
    __tablename__ = 'sheet_status'
    __table_args__ = {'schema': 'meta'}

    status = db.Column(db.String(15), primary_key=True)
    description = db.Column(db.String, nullable=True)
    order = db.Column(db.Integer, nullable=True)

class Notary(db.Model):
    __tablename__ = 'notaries'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    registration_number = db.Column(db.String(255), nullable=False)
    commission_expiration = db.Column(db.Date, nullable=False)
    commission_state = db.Column(db.String(2), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class Circulator(db.Model):
    __tablename__ = 'circulators'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    address_1 = db.Column(db.String(255), nullable=False)
    address_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
