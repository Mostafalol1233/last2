import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_max_attempts_column():
    """Add max_attempts column to the tests table in SQLite database."""
    
    # Determine which database file to use
    instance_db_path = os.path.join(os.getcwd(), 'instance', 'app.db')
    root_db_path = os.path.join(os.getcwd(), 'app.db')
    
    if os.path.exists(instance_db_path) and os.path.getsize(instance_db_path) > 0:
        db_path = instance_db_path
        logger.info(f"Using database from instance folder: {instance_db_path}")
    else:
        db_path = root_db_path
        logger.info(f"Using database from root folder: {root_db_path}")
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(tests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'max_attempts' in columns:
            logger.info("max_attempts column already exists.")
            conn.close()
            return
        
        # Add the column
        logger.info("Adding max_attempts column to tests table...")
        cursor.execute("ALTER TABLE tests ADD COLUMN max_attempts INTEGER DEFAULT 1")
        
        # Update existing records
        cursor.execute("UPDATE tests SET max_attempts = 1")
        
        # Commit changes and close connection
        conn.commit()
        logger.info("Migration completed successfully.")
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_max_attempts_column()