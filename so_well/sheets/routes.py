# so_well/sheets/routes.py
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case
from ..models import db
from .models import Sheet, SheetStatus, Notary, Circulator
from ..signatures.models import SignatureMatch  # Import SignatureMatch
from ..utils import logger

sheets_bp = Blueprint('sheets', __name__, url_prefix='/sheets')


@sheets_bp.route('/', methods=['GET'])
def show_sheets():
    try:
        logger.info('Fetching sheets in Summarizing status with stats')
        summarizing_sheets = db.session.query(
            Sheet.id,
            func.count(SignatureMatch.id).label('total_signatures'),
            func.sum(case((SignatureMatch.voter_id.isnot(None), 1), else_=0)).label('valid_signatures')
        ).join(SignatureMatch, SignatureMatch.sheet_id == Sheet.id).filter(
            Sheet.status == 'Summarizing'
        ).group_by(Sheet.id).all()

        # Append valid_rate to each sheet data
        sheet_data = [
            {
                'sheet_number': sheet[0],
                'total_signatures': sheet[1],
                'valid_signatures': sheet[2],
                'valid_rate': (sheet[2] / sheet[1]) * 100 if sheet[1] > 0 else 0
            }
            for sheet in summarizing_sheets
        ]

        return render_template('sheets.html', sheet_data=sheet_data)
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return render_template('error.html', message='An error occurred while fetching sheets data.'), 500


@sheets_bp.route('/notaries', methods=['GET'])
def get_notaries():
    try:
        logger.info('Fetching notaries')
        notaries = Notary.query.all()
        return jsonify([{'id': notary.id, 'full_name': notary.full_name} for notary in notaries])
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while fetching notaries.'}), 500


@sheets_bp.route('/circulators', methods=['GET'])
def get_circulators():
    try:
        logger.info('Fetching circulators')
        circulators = Circulator.query.all()
        return jsonify([{'id': circulator.id, 'full_name': circulator.full_name} for circulator in circulators])
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while fetching circulators.'}), 500


@sheets_bp.route('/update_sheet_status', methods=['POST'])
def update_sheet_status():
    data = request.json  # Ensure we're receiving the correct data structure
    sheet_number = data.get('sheet_number')
    new_status = data.get('new_status')

    logger.info('Received update request for sheet number: %s to change to status: %s', sheet_number, new_status)

    try:
        sheet = Sheet.query.filter_by(id=sheet_number).first()
        if not sheet:
            logger.warning('Sheet not found for id: %s', sheet_number)
            return jsonify({'error': 'Sheet not found'}), 404

        logger.info('Current status for sheet id: %s is %s', sheet_number, sheet.status)

        valid_transitions = {
            'Printed': 'Signing',
            'Signing': 'Summarizing'
        }

        if sheet.status in valid_transitions and new_status == valid_transitions[sheet.status]:
            sheet.status = new_status
            db.session.commit()
            logger.info('Status updated successfully for sheet id: %s', sheet_number)
            return jsonify({'success': True})
        else:
            logger.warning('Invalid status transition for sheet id: %s from %s to %s', sheet_number, sheet.status, new_status)
            return jsonify({'error': 'Invalid status transition'}), 400

    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while updating the sheet status.'}), 500


@sheets_bp.route('/close_sheet', methods=['POST'])
def close_sheet():
    data = request.json
    sheet_id = data.get('sheet_id')
    notary_id = data.get('notary_id')
    notarized_on = data.get('notarized_on')  # Ensure `notarized_on` is a valid date string
    collector_id = data.get('collector_id')

    logger.info('Received close request for sheet id: %s', sheet_id)

    try:
        sheet = Sheet.query.filter_by(id=sheet_id, status='Summarizing').one_or_none()
        if not sheet:
            logger.warning('Invalid sheet or status for sheet id: %s', sheet_id)
            return jsonify({'error': 'Invalid sheet or status'}), 400

        # Ensure valid integers and date
        if not isinstance(sheet_id, int) or not isinstance(notary_id, int) or not isinstance(collector_id, int):
            logger.warning('Invalid input data for closing sheet')
            return jsonify({'error': 'Invalid input data'}), 400

        logger.info('Closing sheet id: %s', sheet_id)
        sheet.collector_id = collector_id
        sheet.notary_id = notary_id
        sheet.notarized_on = notarized_on
        sheet.status = 'Closed'

        db.session.commit()
        logger.info('Sheet id: %s closed successfully', sheet_id)
        return jsonify({'success': True})

    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while closing the sheet.'}), 500
