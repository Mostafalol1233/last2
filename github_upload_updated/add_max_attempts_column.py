from app import app, db
import logging
import sqlalchemy as sa
from sqlalchemy.sql import text

def add_max_attempts_column():
    """
    Add max_attempts column to the tests table.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        with app.app_context():
            # Check if column exists
            conn = db.engine.connect()
            inspector = sa.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('tests')]
            
            if 'max_attempts' in columns:
                logger.info("max_attempts column already exists in tests table.")
                return
            
            logger.info("Adding max_attempts column to tests table...")
            
            # Add the column
            conn.execute(text('ALTER TABLE tests ADD COLUMN max_attempts INTEGER DEFAULT 1'))
            
            # Set default value for existing records
            conn.execute(text('UPDATE tests SET max_attempts = 1'))
            
            # Commit the changes
            conn.close()
            
            logger.info("Migration completed successfully.")
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    add_max_attempts_column()