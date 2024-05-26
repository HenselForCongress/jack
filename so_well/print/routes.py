# so_well/print/routes.py

from flask import Blueprint, request, render_template, jsonify
from sqlalchemy import text
from ..models import db
from ..utils import logger

print_bp = Blueprint('print_bp', __name__)

@print_bp.route('/print')
def show_print_page():
    return render_template('print.html')

@print_bp.route('/fetch_data', methods=['GET'])
def fetch_data():
    sheet_number = request.args.get('sheet')
    if not sheet_number:
        return jsonify({'error': 'Missing sheet number'}), 400

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

    try:
        result = db.session.execute(search_query, {'sheet_id': sheet_number})
        data = [dict(row) for row in result.mappings()]  # Use mappings() to directly convert rows into dictionaries
        logger.debug(f"Fetched data for sheet {sheet_number}: {data}")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching data for sheet {sheet_number}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch data'}), 500
