from app import app, db
from models import Test, TestQuestion, QuestionChoice
from datetime import datetime

def create_test():
    """إنشاء اختبار جديد مع أسئلة وخيارات"""
    # معلومات الاختبار
    test_title = "اختبار الرياضيات الأساسية"
    test_description = "اختبار أساسيات الرياضيات للصف الأول"
    admin_id = 1  # معرف المسؤول الذي ينشئ الاختبار
    
    with app.app_context():
        # التحقق مما إذا كان الاختبار موجوداً بالفعل
        test = Test.query.filter_by(title=test_title).first()
        
        if not test:
            # إنشاء اختبار جديد
            test = Test(
                title=test_title,
                description=test_description,
                created_by=admin_id,
                is_active=True,
                time_limit_minutes=30,
                passing_score=60
            )
            db.session.add(test)
            db.session.commit()
            print(f'تم إنشاء الاختبار الجديد برقم: {test.id}')
            
            # إضافة أسئلة للاختبار
            questions = [
                {
                    'text': 'كم يساوي 5 + 7؟',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        {'text': '10', 'is_correct': False},
                        {'text': '12', 'is_correct': True},
                        {'text': '13', 'is_correct': False},
                        {'text': '15', 'is_correct': False}
                    ]
                },
                {
                    'text': 'كم يساوي 9 × 8؟',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        {'text': '64', 'is_correct': False},
                        {'text': '72', 'is_correct': True},
                        {'text': '81', 'is_correct': False},
                        {'text': '56', 'is_correct': False}
                    ]
                },
                {
                    'text': 'هل 25 أكبر من 52؟',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        {'text': 'صحيح', 'is_correct': False},
                        {'text': 'خطأ', 'is_correct': True}
                    ]
                },
                {
                    'text': 'ما هي نتيجة 10 ÷ 2؟',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        {'text': '2', 'is_correct': False},
                        {'text': '5', 'is_correct': True},
                        {'text': '8', 'is_correct': False},
                        {'text': '20', 'is_correct': False}
                    ]
                },
                {
                    'text': 'ما هو الوسط الحسابي للأعداد 3, 7, 8, 12?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': '6', 'is_correct': False},
                        {'text': '7.5', 'is_correct': True},
                        {'text': '8', 'is_correct': False},
                        {'text': '10', 'is_correct': False}
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
                
            print(f'تم إضافة {len(questions)} أسئلة للاختبار.')
        else:
            print(f'الاختبار موجود بالفعل برقم: {test.id}')

if __name__ == "__main__":
    create_test()