
import os
from app import app, db
import logging
from test_routes import admin_tests, student_tests

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
    from routes import main_bp, admin_bp, student_bp
    from payment_routes import payment_bp
    from sms_routes import sms_bp
    
    # Register the main blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    
    # Register specialty blueprints
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(sms_bp, url_prefix='/sms')
    
    # Register test blueprints
    app.register_blueprint(admin_tests, url_prefix='/admin/tests')
    app.register_blueprint(student_tests, url_prefix='/student/tests')

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
