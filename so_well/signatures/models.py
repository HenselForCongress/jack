# so_well/signatures/models.py

from sqlalchemy import Column, Integer, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from ..models import db

class SignatureMatch(db.Model):
    __tablename__ = 'matches'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(50), nullable=False)  # Changed to store identification_number
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    full_street_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip = db.Column(db.String(10), nullable=False)
    sheet_number = db.Column(db.Integer, nullable=False)
    row_number = db.Column(db.Integer, nullable=False)  # Keep the check constraint
    #row_number = db.Column(db.Integer, nullable=False, check_column=db.CheckConstraint('row_number >= 1 AND row_number <= 12'))  # Keep the check constraint
    last_four_ssn = db.Column(db.String(4), nullable=True)
    date_collected = db.Column(db.Date, nullable=False, default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<SignatureMatch(Voter ID='{self.voter_id}', Sheet Number='{self.sheet_number}', Row Number='{self.row_number}')>"
