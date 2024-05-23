# so_well/app.py
import os
from flask import Blueprint, render_template, request, g
from .models import db
from .utils import logger
from .middleware import cloudflare_auth_middleware
from .search import search


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

@bp.route('/entry')
def entry():
    return render_template('entry.html')


