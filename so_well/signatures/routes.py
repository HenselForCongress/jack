# so_well/signatures/routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, VoterLookup, Voter
from .models import SignatureMatch
from ..utils import logger

signatures_bp = Blueprint('signatures', __name__, url_prefix='/signatures')

@signatures_bp.route('/verify', methods=['POST'])
def verify_signature():
    try:
        data = request.json
        voter_lookup_id = data.get('voter_id')
        sheet_number = data.get('sheet_number')
        row_number = data.get('row_number')
        last_four_ssn = data.get('last_four_ssn')
        date_collected = data.get('date_collected')

        if not voter_lookup_id or not sheet_number or not row_number or not date_collected:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch voter details from the VoterLookup table
        voter_lookup = VoterLookup.query.filter_by(id=voter_lookup_id).first()
        if not voter_lookup:
            return jsonify({'error': 'Voter lookup entry not found'}), 404

        # Fetch the actual voter details using the identification_number
        voter = Voter.query.filter_by(identification_number=voter_lookup.identification_number).first()
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404

        # Prepare the full street address
        full_street_address = f"{voter_lookup.house_number or ''} {voter_lookup.house_number_suffix or ''} {voter_lookup.direction or ''} {voter_lookup.street_name or ''} {voter_lookup.street_type or ''} {voter_lookup.post_direction or ''}".strip()

        # Create a new SignatureMatch record
        new_signature = SignatureMatch(
            voter_id=voter.identification_number,  # Store the identification_number
            first_name=voter_lookup.first_name,
            last_name=voter_lookup.last_name,
            full_street_address=full_street_address,
            city=voter_lookup.city,
            state=voter_lookup.state,
            zip=voter_lookup.zip,
            sheet_number=int(sheet_number),
            row_number=int(row_number),
            last_four_ssn=last_four_ssn,
            date_collected=date_collected
        )
        db.session.add(new_signature)
        db.session.commit()

        return jsonify({'message': 'Signature verified and recorded successfully'}), 201

    except SQLAlchemyError as e:
        logger.error(f'Error recording signature: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}', exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500
