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

    try:
        data_result = db.session.execute(search_query, {'sheet_id': sheet_number})
        data = [dict(row) for row in data_result.mappings()]

        sheet_result = db.session.execute(sheet_query, {'sheet_id': sheet_number})
        sheet_info = sheet_result.fetchone()

        # Ensure 12 rows, filling missing rows with blank entries
        data_dict = {entry['row']: entry for entry in data}
        full_data = []
        for i in range(1, 13):
            if i in data_dict:
                full_data.append(data_dict[i])
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

        # Convert sheet_info to a dictionary if it's not None
        if sheet_info:
            sheet_info_dict = {column: value for column, value in zip(sheet_result.keys(), sheet_info)}
        else:
            sheet_info_dict = {}

        response = {
            'data': full_data,
            'sheet_info': sheet_info_dict
        }

        logger.debug(f"Fetched data for sheet {sheet_number}: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error fetching data for sheet {sheet_number}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch data'}), 500
