# so_well/app.py
from flask import Blueprint, render_template, jsonify, request
from .utils import logger

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')
