# so_well/batches/routes.py
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case
from ..models import db
from ..sheets.models import Sheet
from ..signatures.models import SignatureMatch
from ..batches.models import Batch, BatchStatus
from ..utils import logger

batches_bp = Blueprint('batches', __name__, url_prefix='/batches')


@batches_bp.route('/', methods=['GET'])
def show_batches():
    try:
        logger.info('Fetching sheets with Closed status')
        closed_sheets = Sheet.query.filter_by(status='Closed').all()
        building_batch = Batch.query.filter_by(status='Building').one_or_none()

        batch_sheets = []
        total_signatures = 0
        total_valid_signatures = 0

        if building_batch:
            logger.info('Fetching sheets in current Building batch')
            batch_sheets_query = db.session.query(
                Sheet.id.label('sheet_number'),
                db.func.count(SignatureMatch.id).label('total_signatures'),
                db.func.sum(case((SignatureMatch.voter_id.isnot(None), 1), else_=0)).label('valid_signatures')
            ).join(SignatureMatch, SignatureMatch.sheet_id == Sheet.id).filter(
                Sheet.batch_id == building_batch.id
            ).group_by(Sheet.id).all()

            for row in batch_sheets_query:
                sheet = {
                    'sheet_number': row.sheet_number,
                    'total_signatures': row.total_signatures,
                    'valid_signatures': row.valid_signatures,
                    'valid_rate': (row.valid_signatures / row.total_signatures) * 100 if row.total_signatures > 0 else 0
                }
                batch_sheets.append(sheet)
                total_signatures += row.total_signatures
                total_valid_signatures += row.valid_signatures

        return render_template(
            'batches.html',
            closed_sheets=closed_sheets,
            building_batch=building_batch,
            batch_sheets=batch_sheets,
            total_signatures=total_signatures,
            total_valid_signatures=total_valid_signatures,
            total_valid_rate=(total_valid_signatures / total_signatures) * 100 if total_signatures > 0 else 0
        )
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return render_template('error.html', message='An error occurred while fetching batches data.'), 500


@batches_bp.route('/add_to_batch', methods=['POST'])
def add_to_batch():
    data = request.json
    try:
        sheet_id = data.get('sheet_id')
        sheet = Sheet.query.filter_by(id=sheet_id, status='Closed').first()
        if not sheet:
            logger.warning('Invalid sheet for adding to batch: %s', sheet_id)
            return jsonify({'error': 'Invalid sheet'}), 400

        batch = Batch.query.filter_by(status='Building').one_or_none()
        if not batch:
            batch = Batch(status='Building')
            db.session.add(batch)
            db.session.flush()  # Ensure id is available for assignment

        sheet.batch_id = batch.id
        sheet.status = 'Pre-shipment'
        db.session.commit()
        logger.info('Sheet %s added to batch %s', sheet.id, batch.id)
        return jsonify({'success': True, 'batch_id': batch.id})
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while adding sheet to batch.'}), 500


@batches_bp.route('/close_batch', methods=['POST'])
def close_batch():
    try:
        batch = Batch.query.filter_by(status='Building').one_or_none()
        if not batch:
            logger.warning('No batch currently being built.')
            return jsonify({'error': 'No batch to close'}), 400

        batch.status = 'Pre-shipment'
        sheets = Sheet.query.filter_by(batch_id=batch.id).all()
        for sheet in sheets:
            sheet.status = 'Pre-shipment'

        db.session.commit()
        logger.info('Batch %s closed', batch.id)
        return jsonify({'success': True, 'batch_id': batch.id})
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while closing the batch.'}), 500


@batches_bp.route('/ship_batch', methods=['POST'])
def ship_batch():
    data = request.json
    try:
        carrier = data.get('carrier')
        tracking_number = data.get('tracking_number')
        ship_date = data.get('ship_date')

        batch = Batch.query.filter_by(status='Pre-shipment').one_or_none()
        if not batch:
            logger.warning('No batch ready for shipment.')
            return jsonify({'error': 'No batch to ship'}), 400

        batch.carrier = carrier
        batch.tracking_number = tracking_number
        batch.ship_date = ship_date
        batch.status = 'Shipped'

        sheets = Sheet.query.filter_by(batch_id=batch.id).all()
        for sheet in sheets:
            sheet.status = 'Shipped'

        db.session.commit()
        logger.info('Batch %s shipped', batch.id)
        return jsonify({'success': True, 'batch_id': batch.id})
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while shipping the batch.'}), 500
