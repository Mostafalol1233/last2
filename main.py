
import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# تكوين التسجيل
logging.basicConfig(level=logging.INFO)

# إنشاء قاعدة بيانات فلاسك
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# تكوين السر
app.secret_key = os.environ.get("SESSION_SECRET", "ahmed-helly-educational-platform-secret-key")

# إضافة معالجات الأخطاء
@app.errorhandler(403)
def forbidden(e):
    logging.error(f"403 Forbidden error: {str(e)}")
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    logging.error(f"404 Page not found error: {str(e)}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"500 Internal server error: {str(e)}")
    return render_template('500.html'), 500

# تكوين قاعدة البيانات
# استخدام SQLite مع مسار مطلق في مجلد قابل للكتابة
db_path = os.path.join(os.getcwd(), 'app.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# تهيئة الإضافات
db.init_app(app)

# إعداد مدير تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# تحميل كل البلوبرنتات
with app.app_context():
    # استيراد النماذج
    import models
    
    # إنشاء الجداول
    db.create_all()
    
    # استيراد الروتات
    from routes import main_bp, admin_bp, student_bp
    from test_routes import admin_tests, student_tests
    import payment_routes
    import sms_routes
    
    # تسجيل البلوبرنتات
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_tests)
    app.register_blueprint(student_tests)
    app.register_blueprint(payment_routes.payment_bp)
    app.register_blueprint(sms_routes.sms_bp)
    
    # دالة تحميل المستخدم
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
        
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
    indicator_file = os.path.join(os.getcwd(), 'first_run_complete.txt')
    if not os.path.exists(indicator_file):
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
