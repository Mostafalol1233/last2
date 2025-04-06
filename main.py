from app import app, db, login_manager
import logging
import os
import models

# تكوين السر
app.secret_key = os.environ.get("SESSION_SECRET", "ahmed-helly-educational-platform-secret-key")

# تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///instance/app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database and load models
with app.app_context():
    db.create_all()

    # Import routes after db initialization
    from routes import main_bp, admin_bp, student_bp
    from test_routes import admin_tests, student_tests
    import payment_routes
    import sms_routes

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_tests)
    app.register_blueprint(student_tests)
    app.register_blueprint(payment_routes.payment_bp)
    app.register_blueprint(sms_routes.sms_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # دالة تحميل المستخدم


    # التحقق من المستخدمين النشطين
    def check_users():
        admin_exists = models.User.query.filter_by(role='admin').first() is not None
        student_exists = models.User.query.filter_by(role='student').first() is not None

        if not admin_exists:
            logging.warning("تنبيه: لا يوجد مستخدم بصلاحية المشرف! استخدم create_users.py لإنشاء مستخدمين.")

        if not student_exists:
            logging.warning("تنبيه: لا يوجد مستخدم بصلاحية الطالب! استخدم create_users.py لإنشاء مستخدمين.")

        active_users = models.User.query.all()
        print("المستخدمون النشطون:")
        print("==================")
        for user in active_users:
            print(f"- {user.full_name or user.username} ({user.username})")
        print("==================")

    # تنفيذ التحقق
    check_users()

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