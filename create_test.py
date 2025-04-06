import os
from flask import Flask
from app import db, app
from models import Test, TestQuestion, QuestionChoice

def create_sample_test():
    """Create a simple math test for testing purposes"""
    
    # تحقق مما إذا كان هناك اختبار بنفس الاسم موجود بالفعل
    existing_test = Test.query.filter_by(title='اختبار الرياضيات البسيط').first()
    if existing_test:
        print("الاختبار الأول موجود بالفعل!")
    else:
        # إنشاء اختبار جديد
        test = Test(
            title='اختبار الرياضيات البسيط',
            description='اختبار في أساسيات الرياضيات وحساب المثلثات',
            time_limit_minutes=30,
            passing_score=60,
            is_active=True,
            created_by=1  # المستخدم رقم 1 (المسؤول)
        )
        db.session.add(test)
        db.session.flush()  # لاستخراج ID الاختبار
        
        # الأسئلة - سؤال 1
        q1 = TestQuestion(
            test_id=test.id,
            question_text='إذا كان طول ضلعي مثلث قائم الزاوية 3 سم و 4 سم، فما هو طول الضلع الثالث (الوتر)؟',
            question_type='multiple_choice',
            points=1,
            order=1
        )
        db.session.add(q1)
        db.session.flush()
        
        # خيارات للسؤال 1
        db.session.add_all([
            QuestionChoice(question_id=q1.id, choice_text='5 سم', is_correct=True, order=1),
            QuestionChoice(question_id=q1.id, choice_text='6 سم', is_correct=False, order=2),
            QuestionChoice(question_id=q1.id, choice_text='7 سم', is_correct=False, order=3),
            QuestionChoice(question_id=q1.id, choice_text='8 سم', is_correct=False, order=4)
        ])
        
        # سؤال 2
        q2 = TestQuestion(
            test_id=test.id,
            question_text='ما هي مساحة مثلث طول قاعدته 6 سم وارتفاعه 8 سم؟',
            question_type='multiple_choice',
            points=1,
            order=2
        )
        db.session.add(q2)
        db.session.flush()
        
        # خيارات للسؤال 2
        db.session.add_all([
            QuestionChoice(question_id=q2.id, choice_text='24 سم²', is_correct=True, order=1),
            QuestionChoice(question_id=q2.id, choice_text='48 سم²', is_correct=False, order=2),
            QuestionChoice(question_id=q2.id, choice_text='12 سم²', is_correct=False, order=3),
            QuestionChoice(question_id=q2.id, choice_text='36 سم²', is_correct=False, order=4)
        ])
        
        # سؤال 3
        q3 = TestQuestion(
            test_id=test.id,
            question_text='إذا كان محيط مربع يساوي 20 سم، فما هي مساحته؟',
            question_type='multiple_choice',
            points=1,
            order=3
        )
        db.session.add(q3)
        db.session.flush()
        
        # خيارات للسؤال 3
        db.session.add_all([
            QuestionChoice(question_id=q3.id, choice_text='25 سم²', is_correct=True, order=1),
            QuestionChoice(question_id=q3.id, choice_text='20 سم²', is_correct=False, order=2),
            QuestionChoice(question_id=q3.id, choice_text='30 سم²', is_correct=False, order=3),
            QuestionChoice(question_id=q3.id, choice_text='100 سم²', is_correct=False, order=4)
        ])
        
        # سؤال 4
        q4 = TestQuestion(
            test_id=test.id,
            question_text='ما هي قيمة جا(٦٠°) ؟',
            question_type='multiple_choice',
            points=1,
            order=4
        )
        db.session.add(q4)
        db.session.flush()
        
        # خيارات للسؤال 4
        db.session.add_all([
            QuestionChoice(question_id=q4.id, choice_text='0.866', is_correct=True, order=1),
            QuestionChoice(question_id=q4.id, choice_text='0.5', is_correct=False, order=2),
            QuestionChoice(question_id=q4.id, choice_text='0.707', is_correct=False, order=3),
            QuestionChoice(question_id=q4.id, choice_text='1', is_correct=False, order=4)
        ])
        
        # سؤال 5
        q5 = TestQuestion(
            test_id=test.id,
            question_text='إذا كان طول ضلع مربع هو a، فما هي صيغة محيطه؟',
            question_type='multiple_choice',
            points=1,
            order=5
        )
        db.session.add(q5)
        db.session.flush()
        
        # خيارات للسؤال 5
        db.session.add_all([
            QuestionChoice(question_id=q5.id, choice_text='4a', is_correct=True, order=1),
            QuestionChoice(question_id=q5.id, choice_text='2a', is_correct=False, order=2),
            QuestionChoice(question_id=q5.id, choice_text='a²', is_correct=False, order=3),
            QuestionChoice(question_id=q5.id, choice_text='4a²', is_correct=False, order=4)
        ])
        
        print(f"تم إنشاء الاختبار الأول بنجاح: {test.title}")
    
    # إنشاء اختبار ثان
    existing_test2 = Test.query.filter_by(title='اختبار الجبر والمعادلات').first()
    if existing_test2:
        print("الاختبار الثاني موجود بالفعل!")
        return existing_test2
    else:
        # إنشاء اختبار جديد
        test2 = Test(
            title='اختبار الجبر والمعادلات',
            description='اختبار في الجبر وحل المعادلات من الدرجة الأولى والثانية',
            time_limit_minutes=40,
            passing_score=70,
            is_active=True,
            created_by=1  # المستخدم رقم 1 (المسؤول)
        )
        db.session.add(test2)
        db.session.flush()  # لاستخراج ID الاختبار
        
        # الأسئلة - سؤال 1
        q1 = TestQuestion(
            test_id=test2.id,
            question_text='حل المعادلة: 2x + 5 = 15',
            question_type='multiple_choice',
            points=1,
            order=1
        )
        db.session.add(q1)
        db.session.flush()
        
        # خيارات للسؤال 1
        db.session.add_all([
            QuestionChoice(question_id=q1.id, choice_text='x = 5', is_correct=True, order=1),
            QuestionChoice(question_id=q1.id, choice_text='x = 7', is_correct=False, order=2),
            QuestionChoice(question_id=q1.id, choice_text='x = 10', is_correct=False, order=3),
            QuestionChoice(question_id=q1.id, choice_text='x = 3', is_correct=False, order=4)
        ])
        
        # سؤال 2
        q2 = TestQuestion(
            test_id=test2.id,
            question_text='حل المعادلة: x² - 9 = 0',
            question_type='multiple_choice',
            points=1,
            order=2
        )
        db.session.add(q2)
        db.session.flush()
        
        # خيارات للسؤال 2
        db.session.add_all([
            QuestionChoice(question_id=q2.id, choice_text='x = ±3', is_correct=True, order=1),
            QuestionChoice(question_id=q2.id, choice_text='x = 3', is_correct=False, order=2),
            QuestionChoice(question_id=q2.id, choice_text='x = ±9', is_correct=False, order=3),
            QuestionChoice(question_id=q2.id, choice_text='x = 9', is_correct=False, order=4)
        ])
        
        # سؤال 3
        q3 = TestQuestion(
            test_id=test2.id,
            question_text='ما هو ناتج تبسيط: (3x + 2) + (4x - 7)',
            question_type='multiple_choice',
            points=1,
            order=3
        )
        db.session.add(q3)
        db.session.flush()
        
        # خيارات للسؤال 3
        db.session.add_all([
            QuestionChoice(question_id=q3.id, choice_text='7x - 5', is_correct=True, order=1),
            QuestionChoice(question_id=q3.id, choice_text='7x + 5', is_correct=False, order=2),
            QuestionChoice(question_id=q3.id, choice_text='7x - 9', is_correct=False, order=3),
            QuestionChoice(question_id=q3.id, choice_text='7x + 9', is_correct=False, order=4)
        ])
        
        # سؤال 4
        q4 = TestQuestion(
            test_id=test2.id,
            question_text='أوجد قيمة a في المعادلة: 2a - 5 = 13',
            question_type='multiple_choice',
            points=1,
            order=4
        )
        db.session.add(q4)
        db.session.flush()
        
        # خيارات للسؤال 4
        db.session.add_all([
            QuestionChoice(question_id=q4.id, choice_text='a = 9', is_correct=True, order=1),
            QuestionChoice(question_id=q4.id, choice_text='a = 4', is_correct=False, order=2),
            QuestionChoice(question_id=q4.id, choice_text='a = 6', is_correct=False, order=3),
            QuestionChoice(question_id=q4.id, choice_text='a = 8', is_correct=False, order=4)
        ])
        
        # سؤال 5
        q5 = TestQuestion(
            test_id=test2.id,
            question_text='ما هي العبارة المكافئة لـ (x² - 4)(x + 2)',
            question_type='multiple_choice',
            points=1,
            order=5
        )
        db.session.add(q5)
        db.session.flush()
        
        # خيارات للسؤال 5
        db.session.add_all([
            QuestionChoice(question_id=q5.id, choice_text='x³ - 8', is_correct=True, order=1),
            QuestionChoice(question_id=q5.id, choice_text='x³ + 8', is_correct=False, order=2),
            QuestionChoice(question_id=q5.id, choice_text='x³ - 4x - 8', is_correct=False, order=3),
            QuestionChoice(question_id=q5.id, choice_text='x³ + 4x - 8', is_correct=False, order=4)
        ])
        
        db.session.commit()
        print(f"تم إنشاء الاختبار الثاني بنجاح: {test2.title}")
        return test2

if __name__ == "__main__":
    with app.app_context():
        create_sample_test()
