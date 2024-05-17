# so_well/app.py
from flask import Blueprint, render_template, request, jsonify, abort, g
from .models import db, Voter, Address, User, VoterLookup, AuditLog, SignatureMatch
from sqlalchemy import func
from .utils import logger
from .middleware import cloudflare_auth_middleware

bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    zero_trust = os.getenv('ZERO_TRUST', 'false').lower() == 'true'
    if zero_trust:
        return cloudflare_auth_middleware()  # Call middleware function explicitly

    user_email = request.headers.get('cf-email', 'local_dev_user@example.com')
    g.user_email = user_email
    logger.info(f"User with email {user_email} is making a request")

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/search', methods=['GET'])
def search():
    criteria = {}
    search_fields = ['first_name', 'last_name', 'street_name', 'city', 'zip', 'house_number', 'direction', 'post_direction', 'apt_num']

    for field in search_fields:
        value = request.args.get(field)
        if value:
            criteria[field] = value.strip()

    # Logging the search criteria
    logger.info(f"Search criteria: {criteria}")

    # Construct full-text search queries
    first_name_query = criteria.get('first_name', '').replace('*', ':*')
    last_name_query = criteria.get('last_name', '').replace('*', ':*')
    address_query = ' '.join([
        criteria.get('house_number', '').replace('*', ':*'),
        criteria.get('street_name', '').replace('*', ':*'),
        criteria.get('direction', '').replace('*', ':*'),
        criteria.get('post_direction', '').replace('*', ':*'),
        criteria.get('apt_num', '').replace('*', ':*')
    ])
    city_query = criteria.get('city', '').replace('*', ':*')
    zip_query = criteria.get('zip', '').replace('*', ':*')

    # Prepare the search query with ranking
    try:
        query = db.session.query(
            VoterLookup,
            func.ts_rank(VoterLookup.address_searchable, func.to_tsquery('english', address_query)).label('rank')
        ).filter(
            VoterLookup.full_name_searchable.op('@@')(func.to_tsquery('english', first_name_query)) |
            VoterLookup.full_name_searchable.op('@@')(func.to_tsquery('english', last_name_query)),
            VoterLookup.address_searchable.op('@@')(func.to_tsquery('english', address_query)),
            VoterLookup.city_searchable.op('@@')(func.to_tsquery('english', city_query)),
            VoterLookup.zip_searchable.op('@@')(func.to_tsquery('simple', zip_query))
        ).order_by(
            func.ts_rank(VoterLookup.address_searchable, func.to_tsquery('english', address_query)).desc()
        ).all()

        # Logging the search query
        logger.debug(f"Search query: {query}")

        data = [{
            "id": voter.identification_number,
            "first_name": voter.first_name,
            "last_name": voter.last_name,
            "address": voter.street_name,
            "city": voter.city,
            "state": "CA",
            "zip": voter.zip,
            "rank": result.rank
        } for voter, result in query]

        return jsonify(data)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your search."}), 500

@bp.route('/verify_signature', methods=['POST'])
def verify_signature():
    data = request.json
    voter_id = data.get('voter_id')
    sheet_number = data.get('sheet_number')
    row_number = data.get('row_number')
    last_four_ssn = data.get('last_four_ssn')

    if not all([voter_id, sheet_number, row_number, last_four_ssn]):
        abort(400, "Missing required fields")

    voter = Voter.query.get(voter_id)
    if not voter:
        abort(404, "Voter not found")

    new_match = SignatureMatch(
        voter_id=voter.identification_number,
        sheet_number=sheet_number,
        row_number=row_number,
        last_four_ssn=last_four_ssn,
        first_name=voter.first_name,
        last_name=voter.last_name,
        house_number=voter.residence_address.house_number,
        street_prefix=voter.residence_address.direction,
        street_name=voter.residence_address.street_name,
        street_suffix=voter.residence_address.post_direction,
        city=voter.residence_address.city,
        state=voter.residence_address.state,
        zip=voter.residence_address.zip
    )

    db.session.add(new_match)
    db.session.commit()

    logger.info(f"Signature matched and recorded for voter ID: {voter_id}")

    return jsonify({"message": "Signature matched and recorded successfully"}), 201
