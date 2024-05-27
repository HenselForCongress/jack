# so_well/advanced_search/routes.py
import re
from flask import Blueprint, request, jsonify
from sqlalchemy import func, distinct, and_
from ..models import db, Voter, Address
from ..utils import logger
from sqlalchemy.dialects import postgresql

advanced_search_bp = Blueprint('advanced_search', __name__, url_prefix='/advanced_search')

def wildcard_to_sql(wildcard):
    """
    Convert user-friendly wildcards to SQL wildcards.
    """
    wildcard = re.sub(r'\*', '%', wildcard)
    wildcard = re.sub(r'\?', '_', wildcard)
    return wildcard.lower()



@advanced_search_bp.route('/', methods=['POST'])
def search_voters():
    try:
        data = request.json
        logger.info("Received search request with data: %s", data)
        filters = []

        if 'first_name' in data and data['first_name']:
            pattern = wildcard_to_sql(data['first_name'])
            filters.append(Voter.first_name.ilike(pattern))
            logger.debug("Filter added for first_name with pattern: %s", pattern)
        if 'middle_name' in data and data['middle_name']:
            pattern = wildcard_to_sql(data['middle_name'])
            filters.append(Voter.middle_name.ilike(pattern))
            logger.debug("Filter added for middle_name with pattern: %s", pattern)
        if 'last_name' in data and data['last_name']:
            pattern = wildcard_to_sql(data['last_name'])
            filters.append(Voter.last_name.ilike(pattern))
            logger.debug("Filter added for last_name with pattern: %s", pattern)
        if 'zip_code' in data and data['zip_code']:
            filters.append(Address.zip.ilike(data['zip_code'] + '%'))
            logger.debug("Filter added for zip_code: %s", data['zip_code'])
        if 'house_number' in data and data['house_number']:
            pattern = wildcard_to_sql(data['house_number'])
            filters.append(Address.house_number.ilike(pattern))
            logger.debug("Filter added for house_number with pattern: %s", pattern)
        if 'house_number_suffix' in data and data['house_number_suffix']:
            pattern = wildcard_to_sql(data['house_number_suffix'])
            filters.append(Address.house_number_suffix.ilike(pattern))
            logger.debug("Filter added for house_number_suffix with pattern: %s", pattern)
        if 'street_name' in data and data['street_name']:
            pattern = wildcard_to_sql(data['street_name'])
            filters.append(Address.street_name.ilike(pattern))
            logger.debug("Filter added for street_name with pattern: %s", pattern)
        if 'street_type' in data and data['street_type']:
            filters.append(Address.street_type.in_(data['street_type']))
            logger.debug("Filter added for street_type: %s", data['street_type'])
        if 'direction' in data and data['direction']:
            filters.append(Address.direction.in_(data['direction']))
            logger.debug("Filter added for direction: %s", data['direction'])
        if 'post_direction' in data and data['post_direction']:
            filters.append(Address.post_direction.in_(data['post_direction']))
            logger.debug("Filter added for post_direction: %s", data['post_direction'])
        if 'apartment_number' in data and data['apartment_number']:
            pattern = wildcard_to_sql(data['apartment_number'])
            filters.append(Address.apt_num.ilike(pattern))
            logger.debug("Filter added for apartment_number with pattern: %s", pattern)
        if 'city' in data and data['city']:
            pattern = wildcard_to_sql(data['city'])
            filters.append(Address.city.ilike(pattern))
            logger.debug("Filter added for city with pattern: %s", pattern)
        if 'state' in data and data['state']:
            pattern = data['state']
            filters.append(Address.state == pattern)
            logger.debug("Filter added for state: %s", pattern)

        query = (db.session.query(Voter, Address)
                 .join(Address, Address.id == Voter.residence_address_id)
                 .filter(and_(*filters))
                 .limit(40))

        # Log the compiled SQL query
        compiled_query = query.statement.compile(dialect=postgresql.dialect())
        logger.debug("Executing search query with SQL: %s", str(compiled_query))

        results = []
        for voter, address in query:
            full_address = f"{address.house_number or ''} {address.house_number_suffix or ''} {address.direction or ''} {address.street_name or ''} {address.street_type or ''} {address.post_direction or ''}".strip()
            results.append({
                'first_name': voter.first_name,
                'middle_name': voter.middle_name,
                'last_name': voter.last_name,
                'suffix': voter.suffix,
                'full_address': full_address,
                'apartment_number': address.apt_num,
                'city': address.city,
                'state': address.state,
                'zip_code': address.zip[:5],
                'status': voter.status,
                'voter_id': voter.identification_number
            })
        logger.info("Found %d results.", len(results))

        # Calculate counts
        try:
            direction_counts = db.session.query(Address.direction).group_by(Address.direction).all()
            post_direction_counts = db.session.query(Address.post_direction).group_by(Address.post_direction).all()
            street_type_counts = db.session.query(Address.street_type).group_by(Address.street_type).all()
        except Exception as e:
            logger.error("Error calculating counts: %s", e)
            return jsonify({
                "error": "An error occurred while calculating counts."
            }), 500

        direction_counts = [{'value': dc[0]} for dc in direction_counts if dc[0] is not None]
        post_direction_counts = [{'value': pdc[0]} for pdc in post_direction_counts if pdc[0] is not None]
        street_type_counts = [{'value': stc[0]} for stc in street_type_counts if stc[0] is not None]

        logger.debug("Calculated counts: direction=%s, post_direction=%s, street_type=%s", direction_counts, post_direction_counts, street_type_counts)

        return jsonify({
            "results": results,
            "direction_counts": direction_counts,
            "post_direction_counts": post_direction_counts,
            "street_type_counts": street_type_counts
        })
    except Exception as e:
        logger.error("Unhandled exception: %s", e)
        return jsonify({
            "error": "An unhandled exception occurred."
        }), 500

@advanced_search_bp.route('/states', methods=['GET'])
def get_states():
    states = db.session.query(distinct(Address.state)).all()
    states = [state[0] for state in states]
    return jsonify(states)

@advanced_search_bp.route('/directions', methods=['GET'])
def get_directions():
    directions = db.session.query(Address.direction, func.count(Address.id)).group_by(Address.direction).filter(Address.direction.isnot(None)).all()
    post_directions = db.session.query(Address.post_direction, func.count(Address.id)).group_by(Address.post_direction).filter(Address.post_direction.isnot(None)).all()

    directions = [{'value': direction[0], 'count': direction[1]} for direction in directions]
    post_directions = [{'value': post_direction[0], 'count': post_direction[1]} for post_direction in post_directions]

    return jsonify({'directions': directions, 'post_directions': post_directions})

@advanced_search_bp.route('/street_types', methods=['GET'])
def get_street_types():
    street_types = db.session.query(Address.street_type, func.count(Address.id)).group_by(Address.street_type).filter(Address.street_type.isnot(None)).all()
    street_types = [{'value': street_type[0], 'count': street_type[1]} for street_type in street_types]
    return jsonify({'street_types': street_types})
