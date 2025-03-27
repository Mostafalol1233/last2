import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configure the database
# Check if we're in production (InfinityFree) or development mode
if os.environ.get("INFINITYFREE") == "true":
    # InfinityFree MySQL configuration
    db_user = os.environ.get("INFINITYFREE_DB_USER")
    db_password = os.environ.get("INFINITYFREE_DB_PASSWORD")
    db_name = os.environ.get("INFINITYFREE_DB_NAME")
    db_host = os.environ.get("INFINITYFREE_DB_HOST", "sql312.infinityfree.com")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    # Turn off debug mode in production
    app.config['DEBUG'] = False
    # Set up a stricter content security policy for production
    app.config['CSRF_ENABLED'] = True
    # Set file upload limit for production
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max upload size
elif os.environ.get("DATABASE_URL") and os.environ.get("DATABASE_URL") != "DATABASE_URL":
    # Use existing PostgreSQL database if available (and not a literal "DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    # Set development environment
    app.config['DEBUG'] = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    # Set file upload limit for development/testing
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB max upload size
else:
    # Fallback to SQLite for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    # Enable debug mode for development
    app.config['DEBUG'] = True
    # Set file upload limit for development
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB max upload size

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

# Set up error handlers
@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(error=str(e)), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Log the error
    logger.error(f"500 error: {str(e)}")
    if request.path.startswith('/api/'):
        return jsonify(error='حدث خطأ داخلي في الخادم'), 500
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith('/api/'):
        return jsonify(error='غير مصرح لك بالوصول إلى هذا المورد'), 403
    return render_template('404.html'), 403

@app.errorhandler(413)
def request_entity_too_large(e):
    if request.path.startswith('/api/'):
        return jsonify(error='حجم الملف المرفوع أكبر من الحد المسموح به'), 413
    return render_template('500.html', error='الملف المرفوع كبير جدًا. الحد الأقصى هو 64 ميجابايت.'), 413

# Import models and routes after initialization to avoid circular imports
with app.app_context():
    import models
    from models import User
    import routes
    
    # Register the blueprints
    app.register_blueprint(routes.main_bp)
    app.register_blueprint(routes.admin_bp, url_prefix='/admin')
    app.register_blueprint(routes.student_bp, url_prefix='/student')
    
    # Create all database tables
    db.create_all()
    
    # Setup the user loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
