#!/usr/bin/env python3
"""Database migration script for handling database schema changes"""

import os
import sys
import logging
from dotenv import load_dotenv
import importlib.util
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

def import_models():
    """Import all model classes from models.py"""
    try:
        # Import the app context
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Get the app context
        app = app_module.app
        
        with app.app_context():
            # Import models module
            spec = importlib.util.spec_from_file_location("models", "models.py")
            models_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(models_module)
            
            # Get all model classes
            model_classes = []
            for name, obj in inspect.getmembers(models_module):
                # Check if it's a SQLAlchemy model class
                if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
                    model_classes.append(obj)
            
            return app, app_module.db, model_classes
    except Exception as e:
        logger.error(f"Error importing models: {e}")
        raise

def run_migrations():
    """Run database migrations"""
    try:
        # Check if DATABASE_URL is set
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL environment variable is not set")
            return False
        
        logger.info(f"Using database: {db_url.split('@')[1] if '@' in db_url else db_url}")
        
        # Import app, db, and model classes
        app, db, model_classes = import_models()
        
        # Log model classes found
        model_names = [model.__name__ for model in model_classes]
        logger.info(f"Found {len(model_classes)} model classes: {', '.join(model_names)}")
        
        with app.app_context():
            # Create tables if they don't exist
            logger.info("Creating database tables if they don't exist...")
            db.create_all()
            logger.info("Database tables created or already exist")
            
            # Here we could add more sophisticated migration logic if needed
            
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database migration...")
    success = run_migrations()
    
    if success:
        logger.info("Database migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Database migration failed")
        sys.exit(1)