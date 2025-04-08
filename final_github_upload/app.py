# This file is kept for backwards compatibility but all functionality has moved to main.py
from main import app, db, logging

# طباعة رسالة بأن الملف قيد الاستخدام
logging.info("Using main.py for application configuration")
