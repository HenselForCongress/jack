# so_well/advanced_search/routes.py
import re
from flask import Blueprint, request, jsonify
from sqlalchemy import func, distinct, and_
from ..models import db, Voter, Address

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
    data = request.json
    filters = []

    if 'first_name' in data and data['first_name']:
        pattern = wildcard_to_sql(data['first_name'])
        filters.append(Voter.first_name.ilike(pattern))
    if 'middle_name' in data and data['middle_name']:
        pattern = wildcard_to_sql(data['middle_name'])
        filters.append(Voter.middle_name.ilike(pattern))
    if 'last_name' in data and data['last_name']:
        pattern = wildcard_to_sql(data['last_name'])
        filters.append(Voter.last_name.ilike(pattern))
    if 'zip_code' in data and data['zip_code']:
        filters.append(Address.zip.ilike(data['zip_code'] + '%'))
    if 'house_number' in data and data['house_number']:
        pattern = wildcard_to_sql(data['house_number'])
        filters.append(Address.house_number.ilike(pattern))
    if 'house_number_suffix' in data and data['house_number_suffix']:
        pattern = wildcard_to_sql(data['house_number_suffix'])
        filters.append(Address.house_number_suffix.ilike(pattern))
    if 'street_name' in data and data['street_name']:
        pattern = wildcard_to_sql(data['street_name'])
        filters.append(Address.street_name.ilike(pattern))
    if 'street_type' in data and data['street_type']:
        pattern = wildcard_to_sql(data['street_type'])
        filters.append(Address.street_type.ilike(pattern))
    if 'direction' in data and data['direction']:
        pattern = data['direction']
        filters.append(Address.direction == pattern)
    if 'post_direction' in data and data['post_direction']:
        pattern = data['post_direction']
        filters.append(Address.post_direction == pattern)
    if 'apartment_number' in data and data['apartment_number']:
        pattern = wildcard_to_sql(data['apartment_number'])
        filters.append(Address.apt_num.ilike(pattern))
    if 'city' in data and data['city']:
        pattern = wildcard_to_sql(data['city'])
        filters.append(Address.city.ilike(pattern))
    if 'state' in data and data['state']:
        pattern = data['state']
        filters.append(Address.state == pattern)

    query = (db.session.query(Voter, Address)
             .join(Address, Address.id == Voter.residence_address_id)
             .filter(and_(*filters))
             .limit(40))

    results = []
    for voter, address in query:
        results.append({
            'first_name': voter.first_name,
            'middle_name': voter.middle_name,
            'last_name': voter.last_name,
            'suffix': voter.suffix,
            'address': f"{address.house_number} {address.street_name} {address.street_type}",
            'city': address.city,
            'state': address.state,
            'zip_code': address.zip[:5],
            'status': voter.status,
            'voter_id': voter.identification_number
        })

    return jsonify(results)

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
