from app import app, db
from models import TestQuestion

with app.app_context():
    # تحديث الصورة للسؤال ذو المعرف 5
    question = TestQuestion.query.filter_by(id=5).first()
    if question:
        question.image_path = 'img/tests/question5.png'
        db.session.commit()
        print(f"تم تحديث صورة السؤال {question.id} بنجاح")
    else:
        print("لم يتم العثور على السؤال رقم 5")