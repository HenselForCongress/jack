# run.py
import os
from so_well import begin_era, logger

def main():
    app = begin_era()  # Begin a new era which setups Flask app
    logger.info("🚀 Starting Donation Reporter")
    try:
        # Hosting the Flask application
        app.run(host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('APP_PORT', 5000)))
        logger.info("😃 Application is up and running smoothly.")
    except Exception as e:
        logger.error("💥 An unexpected error occurred: %s", str(e), exc_info=True)

if __name__ == "__main__":
    main()
