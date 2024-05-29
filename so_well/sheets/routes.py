# so_well/sheets/routes.py
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case, text
from datetime import date
from ..models import db
from .models import Sheet, SheetStatus, Notary, Circulator
from ..signatures.models import SignatureMatch
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

# Lookup Sheets
# Fetch Data Route
@sheets_bp.route('/lookup/fetch_data', methods=['GET'])
def lookup_fetch_data():
    sheet_number = request.args.get('sheet_id')
    if not sheet_number:
        return jsonify({'error': 'Missing sheet number'}), 400

    try:
        response = fetch_sheet_data(sheet_number)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error fetching data for sheet {sheet_number}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch data'}), 500

# Sheet Lookup
@sheets_bp.route('/lookup/', methods=['GET'])
def sheet_lookup():
    sheet_id = request.args.get('sheet_id')
    if not sheet_id:
        return jsonify({"error": "Missing sheet_id parameter"}), 400

    return render_template('sheet_lookup.html', sheet_id=sheet_id)

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
    try:
        sheet_id = int(data.get('sheet_id'))
        notary_id = int(data.get('notary_id'))
        notarized_on = data.get('notarized_on')  # Ensure `notarized_on` is a valid date string
        collector_id = int(data.get('collector_id'))
    except (ValueError, TypeError):
        logger.warning('Invalid input data for closing sheet. Ensure sheet_id, notary_id, and collector_id are integers.')
        return jsonify({'error': 'Invalid input data'}), 400

    logger.info('Received close request for sheet id: %s', sheet_id)

    try:
        sheet = Sheet.query.filter_by(id=sheet_id, status='Summarizing').one_or_none()
        if not sheet:
            logger.warning('Invalid sheet or status for sheet id: %s', sheet_id)
            return jsonify({'error': 'Invalid sheet or status'}), 400

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

def fetch_sheet_data(sheet_number):
    search_query = text("""
        SELECT
            row_id AS row,
            voter_id AS "voterId",
            first_name AS "firstName",
            last_name AS "lastName",
            full_street_address AS "address1",
            apt AS "address2",
            city,
            state,
            zip,
            date_collected AS "dateSigned",
            last_4 AS "ssnLast4"
        FROM
            signatures.collected
        WHERE
            sheet_id = :sheet_id
        ORDER BY
            row_id;
    """)

    sheet_query = text("""
        SELECT
            s.notarized_on,
            c.full_name AS circulator_name,
            c.address_1 AS circulator_address_1,
            c.address_2 AS circulator_address_2,
            c.city AS circulator_city,
            c.state AS circulator_state,
            c.zip AS circulator_zip,
            n.full_name AS notary_name,
            n.registration_number AS notary_registration,
            n.commission_expiration AS notary_expiration,
            n.commission_state AS notary_state
        FROM
            signatures.sheets s
        LEFT JOIN
            signatures.circulators c ON s.collector_id = c.id
        LEFT JOIN
            signatures.notaries n ON s.notary_id = n.id
        WHERE
            s.id = :sheet_id;
    """)
    def serialize_date(value):
        return value.isoformat() if isinstance(value, date) else value

    data_result = db.session.execute(search_query, {'sheet_id': sheet_number})
    data = [dict(row) for row in data_result.mappings()]

    sheet_result = db.session.execute(sheet_query, {'sheet_id': sheet_number})
    sheet_info = sheet_result.fetchone()

    data_dict = {entry['row']: entry for entry in data}
    full_data = []
    for i in range(1, 13):
        if i in data_dict:
            entry = data_dict[i]
            entry['dateSigned'] = serialize_date(entry['dateSigned'])
            full_data.append(entry)
        else:
            full_data.append({
                'row': i,
                'voterId': '',
                'firstName': '',
                'lastName': '',
                'address1': '',
                'address2': '',
                'city': '',
                'state': '',
                'zip': '',
                'dateSigned': '',
                'ssnLast4': ''
            })

    sheet_info_dict = {column: serialize_date(value) for column, value in zip(sheet_result.keys(), sheet_info)} if sheet_info else {}

    response = {
        'data': full_data,
        'sheet_info': sheet_info_dict
    }
    return response

@sheets_bp.route('/get_max_row_number', methods=['GET'])
def get_max_row_number():
    sheet_id = request.args.get('sheet_id')
    if not sheet_id:
        return jsonify({'error': 'Missing sheet ID'}), 400

    max_row_number = db.session.query(func.max(SignatureMatch.row_id)).filter_by(sheet_id=sheet_id).scalar()
    return jsonify({'max_row_number': max_row_number})
