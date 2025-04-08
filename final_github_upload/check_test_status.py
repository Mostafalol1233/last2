from app import app, db
from models import Test

with app.app_context():
    tests = Test.query.all()
    for test in tests:
        print(f'اسم الاختبار: {test.title}, حالة النشاط: {test.is_active}')
