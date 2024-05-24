# so_well/signatures/routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Voter, Address
from .models import SignatureMatch
from ..utils import logger

signatures_bp = Blueprint('signatures', __name__, url_prefix='/signatures')

@signatures_bp.route('/verify', methods=['POST'])
def verify_signature():
    try:
        data = request.json
        voter_identification = data.get('voter_id')
        sheet_id = data.get('sheet_number')  # Align with your actual field names
        row_id = data.get('row_number')  # Align with your actual field names
        last_four_ssn = data.get('last_four_ssn')
        date_collected = data.get('date_collected')

        if not voter_identification or not sheet_id or not row_id or not date_collected:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch voter details from Voters using identification_number
        voter = Voter.query.filter_by(identification_number=voter_identification).first()
        if not voter:
            # If no voter found, set status to 'No Match Found'
            status = 'No Match Found'
            new_signature = SignatureMatch(
                voter_id=None,
                first_name=None,
                last_name=None,
                full_street_address=None,
                apt=None,
                city=None,
                state=None,
                zip=None,
                sheet_id=int(sheet_id),
                row_id=int(row_id),
                last_4=last_four_ssn,
                date_collected=date_collected,
                status=status
            )
            db.session.add(new_signature)
            db.session.commit()
            return jsonify({'message': 'No match found and recorded'}), 201

        address = Address.query.filter_by(id=voter.residence_address_id).first()
        if not address:
            return jsonify({'error': 'Voter address not found'}), 404

        # Prepare the full street address
        full_street_address = f"{address.house_number or ''} {address.house_number_suffix or ''} {address.direction or ''} {address.street_name or ''} {address.street_type or ''} {address.post_direction or ''}".strip()

        # Set status to 'Matched' if voter is found
        status = 'Matched'

        # Create a new SignatureMatch record in the collected table
        new_signature = SignatureMatch(
            voter_id=voter.identification_number,
            first_name=voter.first_name,
            last_name=voter.last_name,
            full_street_address=full_street_address,
            apt=address.apt_num,  # Include apt field if needed
            city=address.city,
            state=address.state,
            zip=address.zip[:5],
            sheet_id=int(sheet_id),
            row_id=int(row_id),
            last_4=last_four_ssn,
            date_collected=date_collected,
            status=status  # Set status here
        )
        db.session.add(new_signature)
        db.session.commit()

        return jsonify({'message': 'Signature matched and recorded successfully'}), 201

    except SQLAlchemyError as e:
        logger.error(f'Error recording signature: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}', exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500
