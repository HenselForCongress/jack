# so_well/search/routes.py
from flask import Blueprint, jsonify, request, g
from sqlalchemy import func, or_
from ..models import db, VoterLookup
from ..utils import logger
from .utils import sanitize_query

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    criteria = {}
    search_fields = ['first_name', 'last_name', 'address', 'city', 'state', 'zip', 'apt_num']

    for field in search_fields:
        value = request.args.get(field)
        if value:
            criteria[field] = sanitize_query(value.strip())

    # Logging the search criteria
    logger.info(f"Search criteria: {criteria}")

    # Construct full-text search queries
    first_name_query = criteria.get('first_name', '').replace('*', ':*')
    last_name_query = criteria.get('last_name', '').replace('*', ':*')
    address_query = criteria.get('address', '').replace('*', ':*')
    city_query = criteria.get('city', '').replace('*', ':*')
    state_query = criteria.get('state', '').replace('*', ':*')
    zip_query = criteria.get('zip', '').replace('*', ':*')
    apt_query = criteria.get('apt_num', '').replace('*', ':*')

    # Prepare the search query with ranking based on the presence of first name, last name, address, etc.
    query = db.session.query(
        VoterLookup,
        func.ts_rank_cd(VoterLookup.full_name_searchable, func.to_tsquery(first_name_query)).label('name_rank'),
        func.ts_rank_cd(VoterLookup.address_searchable, func.to_tsquery(address_query)).label('address_rank')
    ).filter(
        or_(
            VoterLookup.full_name_searchable.op('@@')(func.to_tsquery(first_name_query)),
            VoterLookup.full_name_searchable.op('@@')(func.to_tsquery(last_name_query))
        ),
        VoterLookup.address_searchable.op('@@')(func.to_tsquery(address_query)) if address_query else True,
        VoterLookup.city_searchable.op('@@')(func.to_tsquery(city_query)) if city_query else True,
        VoterLookup.zip_searchable.op('@@')(func.to_tsquery(zip_query)) if zip_query else True
    ).order_by(
        func.ts_rank_cd(VoterLookup.full_name_searchable, func.to_tsquery(first_name_query)).desc(),
        func.ts_rank_cd(VoterLookup.address_searchable, func.to_tsquery(address_query)).desc()
    )

    try:
        results = query.all()

        # Logging the search query
        logger.debug(f"Search query: {results}")

        data = [{
            "id": voter.id,
            "first_name": voter.first_name,
            "last_name": voter.last_name,
            "address": f"{voter.house_number} {voter.direction or ''} {voter.street_name} {voter.post_direction or ''}".strip(),  # Ensure address order is correct
            "apt_num": voter.apt_num,
            "city": voter.city,
            "state": voter.state or "VA",
            "zip": voter.zip,
            "name_rank": name_rank,
            "address_rank": address_rank
        } for voter, name_rank, address_rank in results]

        return jsonify(data)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your search."}), 500
