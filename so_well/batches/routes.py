# so_well/batches/routes.py
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case, join
from ..models import db
from ..sheets.models import Sheet, Circulator
from ..signatures.models import SignatureMatch
from ..batches.models import Batch, BatchStatus
from ..utils import logger

batches_bp = Blueprint('batches', __name__, url_prefix='/batches')

@batches_bp.route('/', methods=['GET'])
def show_batches():
    try:
        logger.info('Fetching sheets with Closed status')

        closed_sheets_query = db.session.query(
            Sheet.id,
            func.count(SignatureMatch.id).label('total_signatures'),
            func.sum(case((SignatureMatch.voter_id.isnot(None), 1), else_=0)).label('valid_signatures'),
            (func.sum(case((SignatureMatch.voter_id.isnot(None), 1), else_=0)) / func.count(SignatureMatch.id) * 100).label('match_rate'),
            Circulator.full_name.label('circulator_name'),
            func.max(SignatureMatch.date_collected).label('max_signed_on')
        ).join(SignatureMatch, SignatureMatch.sheet_id == Sheet.id).join(
            Circulator, Circulator.id == Sheet.collector_id, isouter=True
        ).filter(Sheet.status == 'Closed').group_by(Sheet.id, Circulator.full_name).order_by(Sheet.id.asc()).all()

        closed_sheets = [
            {
                'id': sheet.id,
                'total_signatures': sheet.total_signatures,
                'valid_signatures': sheet.valid_signatures,
                'match_rate': sheet.match_rate,
                'circulator_name': sheet.circulator_name,
                'max_signed_on': sheet.max_signed_on.strftime('%Y-%m-%d') if sheet.max_signed_on else None
            }
            for sheet in closed_sheets_query
        ]

        building_batch = Batch.query.filter_by(status='Building').one_or_none()

        batch_sheets = []
        total_signatures = 0
        total_valid_signatures = 0
        sheet_count = 0  # Initialize sheet count

        if building_batch:
            logger.info('Fetching sheets in current Building batch')
            batch_sheets_query = db.session.query(
                Sheet.id.label('sheet_number'),
                db.func.count(SignatureMatch.id).label('total_signatures'),
                db.func.sum(case((SignatureMatch.voter_id.isnot(None), 1), else_=0)).label('valid_signatures'),
                Circulator.full_name.label('circulator_name'),
                func.max(SignatureMatch.date_collected).label('max_signed_on')
            ).join(SignatureMatch, SignatureMatch.sheet_id == Sheet.id).join(
                Circulator, Circulator.id == Sheet.collector_id, isouter=True
            ).filter(Sheet.batch_id == building_batch.id).group_by(Sheet.id, Circulator.full_name).all()

            for row in batch_sheets_query:
                sheet = {
                    'sheet_number': row.sheet_number,
                    'total_signatures': row.total_signatures,
                    'valid_signatures': row.valid_signatures,
                    'valid_rate': (row.valid_signatures / row.total_signatures) * 100 if row.total_signatures > 0 else 0,
                    'circulator_name': row.circulator_name,
                    'max_signed_on': row.max_signed_on.strftime('%Y-%m-%d') if row.max_signed_on else None
                }
                batch_sheets.append(sheet)
                total_signatures += row.total_signatures
                total_valid_signatures += row.valid_signatures
                sheet_count += 1  # Increment sheet count

        return render_template(
            'batches.html',
            closed_sheets=closed_sheets,
            building_batch=building_batch,
            batch_sheets=batch_sheets,
            total_signatures=total_signatures,
            total_valid_signatures=total_valid_signatures,
            total_valid_rate=(total_valid_signatures / total_signatures) * 100 if total_signatures > 0 else 0,
            sheet_count=sheet_count  # Pass the sheet count to the template
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


@batches_bp.route('/create_batch', methods=['POST'])
def create_batch():
    try:
        logger.info('Attempting to create a new batch with status "Building"')
        batch = Batch(status='Building')
        db.session.add(batch)
        db.session.commit()
        logger.info('Batch %s created', batch.id)
        return jsonify({'success': True, 'batch_id': batch.id})
    except SQLAlchemyError as e:
        logger.error('Database error: %s', e)
        return jsonify({'error': 'An error occurred while creating the batch.'}), 500
    except Exception as e:
        logger.error('Unexpected error: %s', e)
        return jsonify({'error': 'An unexpected error occurred while creating the batch.'}), 500
