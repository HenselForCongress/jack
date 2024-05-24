# so_well/signatures/models.py
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from ..models import db

class SignatureMatch(db.Model):
    __tablename__ = 'collected'
    __table_args__ = {'schema': 'signatures'}

    id = db.Column(db.Integer, primary_key=True)
    sheet_id = db.Column(db.Integer, nullable=False)
    row_id = db.Column(db.Integer, nullable=False)
    voter_id = db.Column(db.String(50), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    full_street_address = db.Column(db.Text, nullable=True)
    apt = db.Column(db.String(50), nullable=True)  # Include apt field
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip = db.Column(db.String(5), nullable=True)
    last_4 = db.Column(db.String(4), nullable=True)
    status = db.Column(db.String(50), nullable=False, server_default='Recorded')
    date_collected = db.Column(db.Date, nullable=False, default=db.func.current_date())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<SignatureMatch(Voter ID='{self.voter_id}', Sheet Number='{self.sheet_id}', Row Number='{self.row_id}')>"
