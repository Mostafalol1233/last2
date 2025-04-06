
import os
from app import app, db
import logging

def check_if_first_run():
    """Check if this is the first run by checking if an indicator file exists"""
    indicator_file = 'instance/first_run_complete.txt'
    if not os.path.exists(indicator_file):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(indicator_file), exist_ok=True)
        
        try:
            # Try to import and run the create_test function
            from create_test import create_sample_test
            with app.app_context():
                test = create_sample_test()
                logging.info(f"Created sample test: {test.title}")
                
            # Create indicator file to avoid running again
            with open(indicator_file, 'w') as f:
                f.write('First run completed at: ' + 
                        __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            logging.info("First run setup completed")
        except Exception as e:
            logging.error(f"Error during first run setup: {str(e)}")

def register_blueprints():
    """Register all application blueprints"""
    # Note: All blueprints are already registered in app.py
    # This function is kept for legacy reasons but doesn't do anything
    pass

if __name__ == "__main__":
    # Register all blueprints
    register_blueprints()
    
    # Check for first run
    check_if_first_run()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
