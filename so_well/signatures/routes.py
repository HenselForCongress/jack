# so_well/signatures/routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Voter, Address
from .models import SignatureMatch
from ..utils import logger
from sqlalchemy import func

signatures_bp = Blueprint('signatures', __name__, url_prefix='/signatures')

@signatures_bp.route('/verify', methods=['POST'])
def verify_signature():
    try:
        data = request.json
        logger.debug(f"Received data for verification: {data}")

        voter_identification = data.get('voter_id')
        sheet_id = data.get('sheet_number')
        row_id = data.get('row_number')
        last_four_ssn = data.get('last_four_ssn')
        date_collected = data.get('date_collected')

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        full_street_address = data.get('address')
        apt = data.get('apartment_number')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        if not sheet_id or not row_id or not date_collected:  # Adjust this condition
            logger.error("Missing required fields")
            return jsonify({'error': 'Missing required fields'}), 400

        logger.debug(f"Fetching voter details for ID: {voter_identification}")
        voter = Voter.query.filter_by(identification_number=voter_identification).first()
        if not voter:
            # If no voter found, set status to 'No Match Found'
            status = 'No Match Found'
            new_signature = SignatureMatch(
                voter_id=None,
                first_name=first_name,
                last_name=last_name,
                full_street_address=full_street_address,
                apt=apt,
                city=city,
                state=state,
                zip=zip_code,
                sheet_id=int(sheet_id),
                row_id=int(row_id),
                last_4=last_four_ssn,
                date_collected=date_collected,
                status=status
            )
            db.session.add(new_signature)
            db.session.commit()

            insert_query = str(new_signature)
            logger.debug(f"No voter found. Inserted new record with SQL: {insert_query}")

            return jsonify({'message': 'No match found and recorded'}), 201

        address = Address.query.filter_by(id=voter.residence_address_id).first()
        if not address:
            logger.error("Voter address not found")
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
            apt=address.apt_num,
            city=address.city,
            state=address.state,
            zip=address.zip[:5],
            sheet_id=int(sheet_id),
            row_id=int(row_id),
            last_4=last_four_ssn,
            date_collected=date_collected,
            status=status
        )
        db.session.add(new_signature)
        db.session.commit()

        insert_query = str(new_signature)
        logger.debug(f"Inserted new signature with SQL: {insert_query}")

        return jsonify({'message': 'Signature matched and recorded successfully'}), 201

    except SQLAlchemyError as e:
        logger.error(f'Error recording signature: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}', exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500

@signatures_bp.route('/stats', methods=['GET'])
def get_signature_stats():
    try:
        stats = db.session.query(
            SignatureMatch.status,
            func.count(SignatureMatch.id).label('count')
        ).group_by(SignatureMatch.status).all()

        stats_data = {status: count for status, count in stats}
        logger.debug(f"Signature stats data: {stats_data}")

        return jsonify(stats_data), 200
    except SQLAlchemyError as e:
        logger.error(f'Error fetching signature stats: {str(e)}', exc_info=True)
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}', exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500
