from app import app, db
from models import Test

with app.app_context():
    tests = Test.query.all()
    print(f'عدد الاختبارات المتاحة: {len(tests)}')
    for test in tests:
        print(f'- {test.title}')
