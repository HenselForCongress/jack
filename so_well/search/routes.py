# so_well/search/routes.py
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from ..models import db
from ..utils import logger
from .utils import sanitize_query

search_bp = Blueprint('search', __name__)

# Calculate combined rank
def get_combined_rank(name_rank, address_rank, first_name_similarity, middle_name_similarity, last_name_similarity):
    return (
        name_rank * 0.4 +
        address_rank * 0.2 +
        first_name_similarity * 0.1 +
        middle_name_similarity * 0.1 +
        last_name_similarity * 0.2
    )

@search_bp.route('/search', methods=['GET'])
def search():
    criteria = {}
    search_fields = ['first_name', 'last_name', 'address', 'city', 'state', 'zip', 'apt_num']

    for field in search_fields:
        value = request.args.get(field)
        if value:
            criteria[field] = sanitize_query(value.strip())

    logger.info(f"Search criteria: {criteria}")

    first_name_query = criteria.get('first_name', '')
    last_name_query = criteria.get('last_name', '')
    address_query = criteria.get('address', '')
    city_query = criteria.get('city', '')
    state_query = criteria.get('state', '')
    zip_query = criteria.get('zip', '')

    try:
        # Using pg_trgm similarity for partial matches and ts_rank_cd for relevance
        query = db.session.query(
            VoterLookup,
            func.ts_rank_cd(VoterLookup.full_name_searchable, func.plainto_tsquery('english', f"{first_name_query} & {last_name_query}")).label('name_rank'),
            func.ts_rank_cd(VoterLookup.address_searchable, func.plainto_tsquery(address_query)).label('address_rank'),
            func.similarity(VoterLookup.first_name, first_name_query).label('first_name_similarity'),
            func.similarity(VoterLookup.middle_name, first_name_query).label('middle_name_similarity'),
            func.similarity(VoterLookup.last_name, last_name_query).label('last_name_similarity')
        ).filter(
            or_(
                VoterLookup.full_name_searchable.op('@@')(func.plainto_tsquery('english', f"{first_name_query} & {last_name_query}")),
                VoterLookup.full_name_searchable.op('@@')(func.plainto_tsquery('english', last_name_query)),
                func.similarity(VoterLookup.first_name, first_name_query) > 0.1,
                func.similarity(VoterLookup.middle_name, first_name_query) > 0.1,
                func.similarity(VoterLookup.last_name, last_name_query) > 0.1
            ),
            VoterLookup.address_searchable.op('@@')(func.plainto_tsquery(address_query)) if address_query else True,
            VoterLookup.city_searchable.op('@@')(func.plainto_tsquery(city_query)) if city_query else True,
            VoterLookup.zip_searchable.op('@@')(func.plainto_tsquery(zip_query)) if zip_query else True
        ).order_by(
            (func.ts_rank_cd(VoterLookup.full_name_searchable, func.plainto_tsquery('english', first_name_query)) +
             func.ts_rank_cd(VoterLookup.full_name_searchable, func.plainto_tsquery('english', last_name_query)) * 2).desc(),
            func.similarity(VoterLookup.first_name, first_name_query).desc(),
            func.similarity(VoterLookup.middle_name, first_name_query).desc(),
            func.similarity(VoterLookup.last_name, last_name_query).desc(),
            func.ts_rank_cd(VoterLookup.address_searchable, func.plainto_tsquery(address_query)).desc()
        ).limit(50)

        logger.debug(f"Search query: {query}")

        results = query.all()

        # Formatted search results
        data = [{
            "id": voter.id,
            "first_name": voter.first_name,
            "middle_name": voter.middle_name,
            "last_name": voter.last_name,
            "address": f"{voter.house_number or ''} {voter.house_number_suffix or ''} {voter.direction or ''} {voter.street_name or ''} {voter.street_type or ''} {voter.post_direction or ''}".strip(),
            "apt_num": voter.apt_num,
            "city": voter.city,
            "state": voter.state,
            "zip": voter.zip[:5],
            "rank": get_combined_rank(
                voter.name_rank,
                voter.address_rank,
                voter.first_name_similarity,
                voter.middle_name_similarity,
                voter.last_name_similarity
            )
        } for voter, voter.name_rank, voter.address_rank, voter.first_name_similarity, voter.middle_name_similarity, voter.last_name_similarity in results]

        # Sort data by rank descending
        data.sort(key=lambda x: x['rank'], reverse=True)

        # Log the formatted results
        logger.debug(f"Formatted search results: {data}")

        return jsonify(data)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your search."}), 500
