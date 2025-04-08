import os

# إعدادات التطبيق
SECRET_KEY = os.environ.get("SESSION_SECRET", "ahmed-helly-educational-platform-secret-key")

# إعدادات قاعدة البيانات
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# إعدادات رفع الملفات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# إعدادات API الخارجية
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")