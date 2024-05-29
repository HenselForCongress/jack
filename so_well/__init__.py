# so_well/__init__.py
import os
from flask import Flask, g
from .utils import configure_logger, logger, loader
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import db, migrate
from .middleware import cloudflare_auth_middleware
from sqlalchemy_utils import database_exists, create_database

def begin_era():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    try:
        # Update database URI to use PostgreSQL
        username = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT')
        database = os.getenv('POSTGRES_DATABASE')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}:{port}/{database}'
    except KeyError as e:
        logger.error(f"Missing environment variable: {str(e)}")
        raise

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # Check if the database exists and create it if it doesn't
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        logger.info(f"Database created at {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Apply the blueprints to the app
    from so_well.app import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    #from .search.routes import search_bp
    #app.register_blueprint(search_bp)

    # Import and register the signatures blueprint
    from .signatures.routes import signatures_bp
    app.register_blueprint(signatures_bp)

    # Import and register the new advanced_search blueprint
    from .advanced_search.routes import advanced_search_bp
    app.register_blueprint(advanced_search_bp)

    # Import and register the new advanced_search blueprint
    from .print.routes import print_bp
    app.register_blueprint(print_bp)

    # Sheets Blueprint
    from .sheets.routes import sheets_bp
    app.register_blueprint(sheets_bp)

    # Batches Blueprint
    from .batches.routes import batches_bp
    app.register_blueprint(batches_bp)


    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Apply the middleware based on ZERO_TRUST environment variable
    zero_trust = os.getenv('ZERO_TRUST', 'false').lower() == 'true'
    if zero_trust:
        app.before_request(cloudflare_auth_middleware())
        #logger.info("Zero Trust authentication enabled.")
    else:
        app.before_request(cloudflare_auth_middleware())
        #logger.info("Zero Trust authentication disabled. Using placeholder authentication.")

    configure_logger()


    return app
