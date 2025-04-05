from app import app, db
from models import Test, TestQuestion, QuestionChoice
import datetime

def create_sample_test():
    # Delete existing tests first
    with app.app_context():
        Test.query.delete()
        TestQuestion.query.delete()
        QuestionChoice.query.delete()
        db.session.commit()
        
        # Create a new test
        test = Test(
            title="اختبار الرياضيات البسيط",
            description="اختبار بسيط للعمليات الحسابية والمثلثات",
            created_by=1,  # admin id
            is_active=True,
            time_limit_minutes=30,
            passing_score=60,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(test)
        db.session.commit()
        
        # إضافة بعض الأسئلة للاختبار
        questions = [
            {
                'text': 'كم يساوي 1 + 1؟',
                'type': 'multiple_choice',
                'points': 1,
                'choices': [
                    {'text': '1', 'is_correct': False},
                    {'text': '2', 'is_correct': True},
                    {'text': '3', 'is_correct': False},
                    {'text': '4', 'is_correct': False}
                ]
            },
            {
                'text': 'كم يساوي 2 × 3؟',
                'type': 'multiple_choice',
                'points': 1,
                'choices': [
                    {'text': '5', 'is_correct': False},
                    {'text': '6', 'is_correct': True},
                    {'text': '7', 'is_correct': False},
                    {'text': '8', 'is_correct': False}
                ]
            },
            {
                'text': 'في مثلث قائم الزاوية طول ضلعيه 3 سم و 4 سم، ما هو طول الوتر (الضلع الثالث)؟',
                'type': 'multiple_choice',
                'points': 1,
                'choices': [
                    {'text': '5 سم', 'is_correct': True},
                    {'text': '6 سم', 'is_correct': False},
                    {'text': '7 سم', 'is_correct': False},
                    {'text': '8 سم', 'is_correct': False}
                ]
            },
            {
                'text': 'هل 10 أكبر من 5؟',
                'type': 'true_false',
                'points': 1,
                'choices': [
                    {'text': 'صحيح', 'is_correct': True},
                    {'text': 'خطأ', 'is_correct': False}
                ]
            },
            {
                'text': 'الصورة التالية تمثل مثلث بأطوال أضلاع a=3, b=4. استخدم نظرية فيثاغورس لإيجاد طول الضلع c:<br><img src="/static/img/triangle.svg" alt="مثلث قائم الزاوية" width="300">',
                'type': 'multiple_choice',
                'points': 1,
                'choices': [
                    {'text': '5', 'is_correct': True},
                    {'text': '6', 'is_correct': False},
                    {'text': '7', 'is_correct': False},
                    {'text': '8', 'is_correct': False}
                ]
            }
        ]
        
        for i, q in enumerate(questions, start=1):
            question = TestQuestion(
                test_id=test.id,
                question_text=q['text'],
                question_type=q['type'],
                points=q['points'],
                order=i
            )
            db.session.add(question)
            db.session.commit()
            
            for j, c in enumerate(q['choices'], start=1):
                choice = QuestionChoice(
                    question_id=question.id,
                    choice_text=c['text'],
                    is_correct=c['is_correct'],
                    order=j
                )
                db.session.add(choice)
            
            db.session.commit()
        
        print(f"تم إنشاء اختبار جديد بنجاح: {test.title}")
        return test

if __name__ == "__main__":
    create_sample_test()