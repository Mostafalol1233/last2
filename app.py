import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
elif os.environ.get("DATABASE_URL") and os.environ.get("DATABASE_URL") != "DATABASE_URL":
    # Use existing PostgreSQL database if available (and not a literal "DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    # Fallback to SQLite for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

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
