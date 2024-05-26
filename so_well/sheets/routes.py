# so_well/sheets/routes.py
# so_well/sheets/routes.py
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from ..models import db
from .models import Sheet, SheetStatus, Notary, Circulator
from ..utils import logger

sheets_bp = Blueprint('sheets', __name__, url_prefix='/sheets')


@sheets_bp.route('/', methods=['GET'])
def show_sheets():
    try:
        logger.info('Fetching status counts')
        status_counts = db.session.query(Sheet.status, db.func.count(Sheet.id)).group_by(Sheet.status).all()
        status_count_dict = {status: count for status, count in status_counts}

        logger.info('Fetching ordered statuses')
        ordered_statuses = db.session.query(SheetStatus).order_by(SheetStatus.order).all()

        return render_template('sheets.html', status_counts=status_count_dict, ordered_statuses=ordered_statuses)
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
    data = request.json
    sheet_number = data.get('sheet_number')
    new_status = data.get('new_status')

    logger.info('Received update request for sheet number: %s', sheet_number)

    try:
        sheet = Sheet.query.filter_by(id=sheet_number).first()
        if not sheet:
            logger.warning('Sheet not found for id: %s', sheet_number)
            return jsonify({'error': 'Sheet not found'}), 404

        logger.info('Updating status for sheet id: %s from %s to %s', sheet_number, sheet.status, new_status)
        if (
            (sheet.status == 'Printed' and new_status == 'Signing') or
            (sheet.status == 'Signing' and new_status == 'Summarizing')
        ):
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
    notarized_on = data.get('notarized_on')
    collector_id = data.get('collector_id')

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
