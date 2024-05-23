# so_well/advanced_search/routes.py
import re
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
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
    if 'last_name' in data and data['last_name']:
        pattern = wildcard_to_sql(data['last_name'])
        filters.append(Voter.last_name.ilike(pattern))
    # Add other fields similarly

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
            'address': f"{address.house_number} {address.street_name} {address.street_type}",
            'city': address.city,
            'state': address.state,
            'zip_code': address.zip,
            'status': voter.status,
            'voter_id': voter.identification_number
        })

    return jsonify(results)
