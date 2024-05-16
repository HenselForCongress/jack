# so_well/__init__.py
import os
from flask import Flask
from .utils.logging import configure_logger, logger
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Setup Database and Migration
db = SQLAlchemy()
migrate = Migrate()

def begin_era():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    try:
        # Update database URI to use PostgreSQL
        username = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        # host = os.getenv('POSTGRES_HOST')
        host = 'localhost'
        port = 5431
        # port = os.getenv('POSTGRES_PORT')
        database = os.getenv('POSTGRES_DATABASE')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}:{port}/{database}'
    except KeyError as e:
        logger.error(f"Missing environment variable: {str(e)}")
        raise

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # Apply the blueprints to the app
    from so_well.app import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    configure_logger()
    logger.info("🚀 Flask application configured and ready with PostgreSQL.")

    return app
