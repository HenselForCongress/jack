# so_well/batches/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, backref
from ..models import db

class Batch(db.Model):
    __tablename__ = 'batches'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(255), nullable=True)
    tracking_number = db.Column(db.String(255), nullable=True)
    ship_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    arrival_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    sheets = relationship('Sheet', backref=backref('batch', lazy=True))

class BatchStatus(db.Model):
    __tablename__ = 'batch_status'
    __table_args__ = {'schema': 'meta'}

    status = db.Column(db.String(15), primary_key=True)
    description = db.Column(db.String, nullable=True)
    order = db.Column(db.Integer, nullable=True)
