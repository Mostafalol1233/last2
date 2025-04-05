"""
هذا الملف يحتوي على routes الخاصة بالاختبارات سواء للمسؤول أو للطلاب
"""

import os
import re
import tempfile
import io
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

# استيراد مكتبات معالجة الملفات
from pypdf import PdfReader
import docx

from app import db
from models import Test, TestQuestion, QuestionChoice, TestAttempt, TestAnswer, DirectMessage # Added DirectMessage import
from forms import (
    TestCreateForm as TestForm, 
    TestQuestionForm, 
    QuestionChoiceForm, 
    TestAnswerForm, 
    TestAttemptForm, 
    TestTakingForm
)

# تحديد الأنماط للإجابات المحتملة
CHOICE_PATTERNS = [
    r'\b([A-Dأ-د])[\.:\-\)\s]\s*(.*)', # نمط للإجابات المحتملة (A, ب، الخ)
    r'(\d+)[\.:\-\)\s]\s*(.*)'         # نمط للإجابات الرقمية (1, 2, 3, الخ)
]

# أنماط للأسئلة
QUESTION_PATTERNS = [
    r'(?:السؤال|سؤال).*?(\d+).*?[:.\-]\s*(.*)', # صيغة "السؤال 1: ..."
    r'(\d+)\s*[\.:\-\)\(\]]\s*(.*)',             # صيغة "1. ..."
    r'[^\n]+\?'                                  # أي سطر ينتهي بعلامة استفهام
]

# أنماط للإجابات الصحيحة
CORRECT_ANSWER_PATTERNS = [
    r'الإجابة\s*(?:الصحيحة|الصحيحه).*?[:.\-]\s*([A-Dأ-د\d])',
    r'إجابة\s*(?:صحيحة|صحيحه).*?[:.\-]\s*([A-Dأ-د\d])',
    r'(?:الإجابة|الاجابة).*?[:.\-]\s*([A-Dأ-د\d])'
]

def extract_text_from_pdf(pdf_file):
    """استخراج النص من ملف PDF"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n\n"
    return text

def extract_text_from_docx(docx_file):
    """استخراج النص من ملف Word"""
    doc = docx.Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def find_questions_and_choices(text):
    """
    البحث عن الأسئلة والخيارات في النص
    تعيد قائمة من الأسئلة حيث كل سؤال هو قاموس يحتوي على:
    - question_text: نص السؤال
    - choices: قائمة من الخيارات (كل خيار هو قاموس يحتوي على النص والحالة)
    - question_type: نوع السؤال (multiple_choice, true_false, short_answer)
    """
    questions = []
    lines = text.split('\n')
    current_question = None
    in_choices = False
    choices = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # التحقق من وجود سؤال جديد
        is_question = False
        for pattern in QUESTION_PATTERNS:
            match = re.search(pattern, line)
            if match:
                # إذا كان هناك سؤال حالي، أضفه مع خياراته
                if current_question:
                    # تحديد نوع السؤال
                    question_type = 'multiple_choice'
                    if len(choices) == 2 and any('صح' in c['text'].lower() for c in choices) and any('خطأ' in c['text'].lower() for c in choices):
                        question_type = 'true_false'
                    elif not choices:
                        question_type = 'short_answer'

                    questions.append({
                        'question_text': current_question,
                        'choices': choices,
                        'question_type': question_type
                    })

                # استخراج نص السؤال
                if len(match.groups()) > 1:
                    q_num, q_text = match.groups()
                    current_question = f"{q_text}"
                else:
                    current_question = line

                choices = []
                in_choices = True
                is_question = True
                break

        if is_question:
            continue

        # التحقق من وجود خيارات إذا كنا في سياق سؤال
        if in_choices and current_question:
            for pattern in CHOICE_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    choice_marker, choice_text = match.groups()
                    choices.append({
                        'text': choice_text.strip(),
                        'is_correct': False  # سيتم تحديده لاحقًا
                    })
                    break

            # التحقق من وجود إشارة للإجابة الصحيحة
            for pattern in CORRECT_ANSWER_PATTERNS:
                match = re.search(pattern, line)
                if match and choices:
                    correct_marker = match.group(1)
                    # تحديد أي من الخيارات هو الصحيح بناءً على العلامة
                    for j, choice in enumerate(choices):
                        if correct_marker.isdigit() and j + 1 == int(correct_marker):
                            choice['is_correct'] = True
                        elif not correct_marker.isdigit() and choice.get('marker') == correct_marker:
                            choice['is_correct'] = True

    # إضافة آخر سؤال إذا وجد
    if current_question:
        question_type = 'multiple_choice'
        if len(choices) == 2 and any('صح' in c['text'].lower() for c in choices) and any('خطأ' in c['text'].lower() for c in choices):
            question_type = 'true_false'
        elif not choices:
            question_type = 'short_answer'

        questions.append({
            'question_text': current_question,
            'choices': choices,
            'question_type': question_type
        })

    return questions

def process_test_file(file, test_id):
    """
    معالجة ملف الاختبار وإنشاء الأسئلة والخيارات
    """
    # تحديد نوع الملف والتعامل معه
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    # استخراج النص من الملف
    text = ""
    if file_extension == 'pdf':
        # حفظ الملف مؤقتًا على القرص ثم قراءته
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            file.save(temp.name)
            temp_name = temp.name

        text = extract_text_from_pdf(temp_name)
        os.unlink(temp_name)  # حذف الملف المؤقت

    elif file_extension in ['doc', 'docx']:
        # حفظ الملف مؤقتًا على القرص ثم قراءته
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp:
            file.save(temp.name)
            temp_name = temp.name

        text = extract_text_from_docx(temp_name)
        os.unlink(temp_name)  # حذف الملف المؤقت

    else:
        raise ValueError(f'نوع الملف غير مدعوم: {file_extension}. يرجى استخدام ملفات PDF أو Word.')

    # استخراج الأسئلة والخيارات من النص
    questions_data = find_questions_and_choices(text)

    # إذا لم يتم العثور على أي أسئلة
    if not questions_data:
        raise ValueError('لم يتم العثور على أي أسئلة في الملف. تأكد من تنسيق الملف بشكل صحيح.')

    # إنشاء الأسئلة في قاعدة البيانات
    for i, q_data in enumerate(questions_data, 1):
        question = TestQuestion(
            test_id=test_id,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            points=1,  # يمكن تعديله لاحقًا
            order=i
        )
        db.session.add(question)
        db.session.flush()  # للحصول على معرف السؤال

        # إنشاء الخيارات للسؤال
        for j, choice_data in enumerate(q_data['choices'], 1):
            choice = QuestionChoice(
                question_id=question.id,
                choice_text=choice_data['text'],
                is_correct=choice_data['is_correct'],
                order=j
            )
            db.session.add(choice)

        # إذا كان السؤال من نوع صح/خطأ ولم يتم العثور على خيارات، إنشاء خيارات افتراضية
        if q_data['question_type'] == 'true_false' and not q_data['choices']:
            # خيار "صح"
            choice_true = QuestionChoice(
                question_id=question.id,
                choice_text='صح',
                is_correct=True,  # افتراضي، يمكن تعديله
                order=1
            )
            db.session.add(choice_true)

            # خيار "خطأ"
            choice_false = QuestionChoice(
                question_id=question.id,
                choice_text='خطأ',
                is_correct=False,
                order=2
            )
            db.session.add(choice_false)

    db.session.commit()
    return len(questions_data)  # إرجاع عدد الأسئلة التي تم إنشاؤها

# إنشاء Blueprints للطلاب والمسؤولين
admin_tests = Blueprint('admin_tests', __name__)
student_tests = Blueprint('student_tests', __name__)

#################
# Admin Routes #
#################

@admin_tests.route('/admin/tests')
@login_required
def manage_tests():
    """عرض صفحة إدارة الاختبارات للمسؤول"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    tests = Test.query.filter_by(created_by=current_user.id).order_by(Test.created_at.desc()).all()
    return render_template('admin/tests.html', tests=tests)

@admin_tests.route('/admin/tests/create', methods=['GET', 'POST'])
@login_required
def create_test():
    """إنشاء اختبار جديد"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    form = TestForm()

    if form.validate_on_submit():
        test = Test(
            title=form.title.data,
            description=form.description.data,
            created_by=current_user.id,
            time_limit_minutes=form.time_limit_minutes.data,
            passing_score=form.passing_score.data,
            is_active=form.is_active.data
        )
        db.session.add(test)
        db.session.commit()

        # معالجة الملف المرفوع
        if form.test_file.data:
            test_file = form.test_file.data

            # استدعاء الوظيفة التي تقوم باستخراج الأسئلة من الملف
            try:
                process_test_file(test_file, test.id)
                flash('تم إنشاء الاختبار واستخراج الأسئلة من الملف بنجاح.', 'success')
            except Exception as e:
                flash(f'تم إنشاء الاختبار ولكن حدث خطأ في معالجة الملف: {str(e)}', 'warning')
        else:
            flash('تم إنشاء الاختبار بنجاح. يمكنك الآن إضافة الأسئلة.', 'success')

        return redirect(url_for('admin_tests.edit_test', test_id=test.id))

    return render_template('admin/create_test.html', form=form)

@admin_tests.route('/admin/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    """تحرير تفاصيل الاختبار وإدارة الأسئلة"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    test = Test.query.get_or_404(test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتحرير هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    # نستخدم TestCreateForm لضمان وجود حقل رفع الملف
    form = TestForm(obj=test)
    question_form = TestQuestionForm()

    if form.validate_on_submit():
        form.populate_obj(test)
        db.session.commit()

        # معالجة الملف المرفوع إذا وجد
        if form.test_file.data:
            test_file = form.test_file.data

            # استدعاء الوظيفة التي تقوم باستخراج الأسئلة من الملف
            try:
                num_questions = process_test_file(test_file, test.id)
                flash(f'تم تحديث تفاصيل الاختبار واستخراج {num_questions} أسئلة من الملف بنجاح.', 'success')
            except Exception as e:
                flash(f'تم تحديث تفاصيل الاختبار ولكن حدث خطأ في معالجة الملف: {str(e)}', 'warning')
        else:
            flash('تم تحديث تفاصيل الاختبار بنجاح.', 'success')

        return redirect(url_for('admin_tests.edit_test', test_id=test.id))

    return render_template('admin/edit_test.html', test=test, form=form, question_form=question_form)

@admin_tests.route('/admin/tests/<int:test_id>/delete', methods=['POST'])
@login_required
def delete_test(test_id):
    """حذف اختبار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    test = Test.query.get_or_404(test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لحذف هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    # حذف الاختبار (سيتم حذف الأسئلة والمحاولات تلقائيًا بسبب cascade)
    db.session.delete(test)
    db.session.commit()

    flash('تم حذف الاختبار بنجاح.', 'success')
    return redirect(url_for('admin_tests.manage_tests'))

@admin_tests.route('/admin/tests/<int:test_id>/add_question', methods=['POST'])
@login_required
def add_question(test_id):
    """إضافة سؤال جديد للاختبار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    test = Test.query.get_or_404(test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتعديل هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    form = TestQuestionForm()

    if form.validate_on_submit():
        # حساب الترتيب التالي للسؤال
        max_order = db.session.query(func.max(TestQuestion.order)).filter_by(test_id=test.id).scalar()
        next_order = 1 if max_order is None else max_order + 1

        question = TestQuestion(
            test_id=test.id,
            question_text=form.question_text.data,
            question_type=form.question_type.data,
            points=form.points.data,
            order=next_order
        )
        db.session.add(question)
        db.session.commit()

        flash('تم إضافة السؤال بنجاح. قم بإضافة خيارات الإجابة الآن.', 'success')
        return redirect(url_for('admin_tests.edit_question', question_id=question.id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'خطأ في الحقل {getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('admin_tests.edit_test', test_id=test.id))

@admin_tests.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """تحرير سؤال وإدارة خياراته"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    question = TestQuestion.query.get_or_404(question_id)
    test = Test.query.get_or_404(question.test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتحرير هذا السؤال', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    form = TestQuestionForm(obj=question)
    choice_form = QuestionChoiceForm()

    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('تم تحديث السؤال بنجاح.', 'success')
        return redirect(url_for('admin_tests.edit_question', question_id=question.id))

    return render_template('admin/edit_question.html', question=question, form=form, choice_form=choice_form)

@admin_tests.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    """حذف سؤال"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    question = TestQuestion.query.get_or_404(question_id)
    test = Test.query.get_or_404(question.test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لحذف هذا السؤال', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    test_id = question.test_id

    # حذف السؤال (سيتم حذف الخيارات تلقائيًا بسبب cascade)
    db.session.delete(question)
    db.session.commit()

    # إعادة ترتيب الأسئلة المتبقية
    remaining_questions = TestQuestion.query.filter_by(test_id=test_id).order_by(TestQuestion.order).all()
    for i, q in enumerate(remaining_questions, 1):
        q.order = i
    db.session.commit()

    flash('تم حذف السؤال بنجاح.', 'success')
    return redirect(url_for('admin_tests.edit_test', test_id=test_id))

@admin_tests.route('/admin/questions/<int:question_id>/add_choice', methods=['POST'])
@login_required
def add_choice(question_id):
    """إضافة خيار جديد للسؤال"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    question = TestQuestion.query.get_or_404(question_id)
    test = Test.query.get_or_404(question.test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتعديل هذا السؤال', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    form = QuestionChoiceForm()

    if form.validate_on_submit():
        # حساب الترتيب التالي للخيار
        max_order = db.session.query(func.max(QuestionChoice.order)).filter_by(question_id=question.id).scalar()
        next_order = 1 if max_order is None else max_order + 1

        choice = QuestionChoice(
            question_id=question.id,
            choice_text=form.choice_text.data,
            is_correct=form.is_correct.data,
            order=next_order
        )
        db.session.add(choice)

        # إذا كان السؤال من نوع صح/خطأ، تأكد من أن هناك إجابة واحدة صحيحة فقط
        if question.question_type == 'true_false' and form.is_correct.data:
            for other_choice in question.choices:
                if other_choice != choice:
                    other_choice.is_correct = False

        db.session.commit()

        flash('تم إضافة الخيار بنجاح.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'خطأ في الحقل {getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('admin_tests.edit_question', question_id=question.id))

@admin_tests.route('/admin/choices/<int:choice_id>/edit', methods=['POST'])
@login_required
def edit_choice(choice_id):
    """تحرير خيار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    choice = QuestionChoice.query.get_or_404(choice_id)
    question = TestQuestion.query.get_or_404(choice.question_id)
    test = Test.query.get_or_404(question.test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتحرير هذا الخيار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    choice_text = request.form.get('choice_text')
    is_correct = 'is_correct' in request.form

    if choice_text:
        choice.choice_text = choice_text
        choice.is_correct = is_correct

        # إذا كان السؤال من نوع صح/خطأ، تأكد من أن هناك إجابة واحدة صحيحة فقط
        if question.question_type == 'true_false' and is_correct:
            for other_choice in question.choices:
                if other_choice != choice:
                    other_choice.is_correct = False

        db.session.commit()
        flash('تم تحديث الخيار بنجاح.', 'success')
    else:
        flash('نص الخيار مطلوب.', 'danger')

    return redirect(url_for('admin_tests.edit_question', question_id=question.id))

@admin_tests.route('/admin/choices/<int:choice_id>/delete', methods=['POST'])
@login_required
def delete_choice(choice_id):
    """حذف خيار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    choice = QuestionChoice.query.get_or_404(choice_id)
    question = TestQuestion.query.get_or_404(choice.question_id)
    test = Test.query.get_or_404(question.test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لحذف هذا الخيار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    question_id = choice.question_id

    # حذف الخيار
    db.session.delete(choice)
    db.session.commit()

    # إعادة ترتيب الخيارات المتبقية
    remaining_choices = QuestionChoice.query.filter_by(question_id=question_id).order_by(QuestionChoice.order).all()
    for i, c in enumerate(remaining_choices, 1):
        c.order = i
    db.session.commit()

    flash('تم حذف الخيار بنجاح.', 'success')
    return redirect(url_for('admin_tests.edit_question', question_id=question_id))

@admin_tests.route('/admin/tests/<int:test_id>/results')
@login_required
def test_results(test_id):
    """عرض نتائج الاختبار للمسؤول"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    test = Test.query.get_or_404(test_id)

    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لعرض نتائج هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))

    # جلب جميع محاولات الاختبار المكتملة مرتبة بالتاريخ
    attempts = TestAttempt.query.filter_by(test_id=test_id, completed_at=not None).order_by(TestAttempt.completed_at.desc()).all()

    # حساب إحصائيات الاختبار
    total_attempts = len(attempts)
    passed_attempts = sum(1 for a in attempts if a.passed)
    average_score = sum(a.score for a in attempts) / total_attempts if total_attempts > 0 else 0

    return render_template(
        'admin/test_results.html',
        test=test,
        attempts=attempts,
        total_attempts=total_attempts,
        passed_attempts=passed_attempts,
        average_score=average_score
    )

#################
# Student Routes #
#################

@student_tests.route('/tests')
@login_required
def available_tests():
    """عرض الاختبارات المتاحة للطالب"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط. استخدم واجهة الإدارة للوصول إلى الاختبارات.', 'warning')
        return redirect(url_for('admin.dashboard'))

    # الاختبارات النشطة فقط
    tests = Test.query.filter_by(is_active=True).all()

    # جلب محاولات الطالب لكل اختبار
    all_attempts = TestAttempt.query.filter_by(user_id=current_user.id).all()

    # تنظيم المحاولات حسب الاختبار
    attempts_by_test = {}
    for attempt in all_attempts:
        if attempt.test_id not in attempts_by_test:
            attempts_by_test[attempt.test_id] = []
        attempts_by_test[attempt.test_id].append(attempt)

    # المحاولات المكتملة فقط للعرض في جدول السجل
    completed_attempts = [a for a in all_attempts if a.completed_at is not None]
    completed_attempts.sort(key=lambda x: x.completed_at, reverse=True)

    return render_template(
        'student/tests.html',
        tests=tests,
        attempts_by_test=attempts_by_test,
        completed_attempts=completed_attempts[:10]  # آخر 10 محاولات مكتملة فقط
    )

@student_tests.route('/tests/<int:test_id>/start', methods=['GET'])
@login_required
def start_test(test_id):
    """Create test attempt and show start page"""
    test = Test.query.get_or_404(test_id)

    # Check if test is active
    if not test.is_active:
        flash('هذا الاختبار غير متاح حاليًا.', 'warning')
        return redirect(url_for('student_tests.available_tests'))

    # Check if there's already an in-progress attempt
    existing_attempt = TestAttempt.query.filter_by(
        test_id=test_id, 
        user_id=current_user.id, 
        completed_at=None
    ).first()

    if existing_attempt:
        # Resume existing attempt
        return render_template('student/start_test.html', test=test, attempt=existing_attempt)

    # Create new attempt
    attempt = TestAttempt(
        test_id=test_id,
        user_id=current_user.id,
        started_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()

    # إنشاء إجابات فارغة لجميع أسئلة الاختبار
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    for question in questions:
        answer = TestAnswer(
            attempt_id=attempt.id,
            question_id=question.id
        )
        db.session.add(answer)

    db.session.commit()

    return render_template('student/start_test.html', test=test, attempt=attempt)


@student_tests.route('/attempt/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
def take_test(attempt_id):
    """صفحة أداء الاختبار"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))

    # جلب المحاولة والتحقق من ملكيتها
    attempt = TestAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id:
        flash('ليس لديك صلاحية للوصول إلى هذه المحاولة.', 'danger')
        return redirect(url_for('student_tests.available_tests'))

    # التحقق من أن المحاولة لم تكتمل بعد
    if attempt.completed_at is not None:
        flash('تم إكمال هذه المحاولة بالفعل. يمكنك الاطلاع على النتائج.', 'info')
        return redirect(url_for('student_tests.test_results', attempt_id=attempt.id))

    test = Test.query.get_or_404(attempt.test_id)

    # حساب الوقت المتبقي
    total_seconds = test.time_limit_minutes * 60
    elapsed_seconds = (datetime.utcnow() - attempt.started_at).total_seconds()

    if elapsed_seconds >= total_seconds:
        # انتهى الوقت، إكمال الاختبار تلقائيًا
        attempt.completed_at = datetime.utcnow()
        attempt.score = attempt.calculate_score()
        attempt.passed = attempt.score >= test.passing_score
        db.session.commit()

        flash('انتهى وقت الاختبار وتم تسليمه تلقائيًا.', 'warning')
        return redirect(url_for('student_tests.test_results', attempt_id=attempt.id))

    seconds_remaining = total_seconds - int(elapsed_seconds)

    # جلب الأسئلة بترتيبها
    questions = TestQuestion.query.filter_by(test_id=test.id).order_by(TestQuestion.order).all()

    # جلب الإجابات الحالية
    answers_query = TestAnswer.query.filter_by(attempt_id=attempt.id)
    answers = {answer.question_id: answer for answer in answers_query.all()}

    # معالجة تسليم النموذج
    if request.method == 'POST':
        action = request.form.get('action', 'save')

        # حفظ الإجابات
        for question in questions:
            answer_value = request.form.get(f'question_{question.id}')
            answer = answers.get(question.id)

            if answer and answer_value:
                if question.question_type in ['multiple_choice', 'true_false']:
                    choice = QuestionChoice.query.get(int(answer_value))
                    answer.selected_choice_id = choice.id
                    answer.is_correct = choice.is_correct
                elif question.question_type == 'short_answer':
                    answer.text_answer = answer_value

        db.session.commit()

        # إذا كان طلب AJAX (الحفظ التلقائي)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'تم حفظ الإجابات'})

        if action == 'submit':
            # Submit the test and calculate score
            attempt.completed_at = datetime.utcnow()
            attempt.score = attempt.calculate_score()
            attempt.passed = attempt.score >= test.passing_score
            db.session.commit()

            # Send notification to admin
            admin_msg = DirectMessage(
                sender_id=current_user.id,
                recipient_id=test.created_by,
                message=f"تم إكمال الاختبار {test.title} بنتيجة {attempt.score}% {'(ناجح)' if attempt.passed else '(راسب)'}"
            )
            db.session.add(admin_msg)

            # Send notification to student
            student_msg = DirectMessage(
                sender_id=test.created_by,
                recipient_id=current_user.id,
                message=f"نتيجة اختبار {test.title}: {attempt.score}% {'مبروك النجاح!' if attempt.passed else 'حظ أوفر في المرة القادمة.'}"
            )
            db.session.add(student_msg)
            db.session.commit()

            flash('تم تسليم الاختبار بنجاح! يمكنك الآن مشاهدة نتيجتك.', 'success')
            return redirect(url_for('student_tests.test_results', attempt_id=attempt.id))

        flash('تم حفظ إجاباتك. يمكنك متابعة الاختبار.', 'success')

    form = TestAnswerForm()  # نموذج فارغ للـ CSRF

    return render_template(
        'student/take_test.html',
        test=test,
        attempt=attempt,
        questions=questions,
        answers=answers,
        seconds_remaining=seconds_remaining,
        form=form
    )

@student_tests.route('/attempt/<int:attempt_id>/results')
@login_required
def test_results(attempt_id):
    """عرض نتائج محاولة اختبار"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))

    # جلب المحاولة والتحقق من ملكيتها
    attempt = TestAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id:
        flash('ليس لديك صلاحية للوصول إلى هذه النتائج.', 'danger')
        return redirect(url_for('student_tests.available_tests'))

    # التحقق من أن المحاولة مكتملة
    if attempt.completed_at is None:
        flash('لم يتم إكمال هذه المحاولة بعد.', 'warning')
        return redirect(url_for('student_tests.take_test', attempt_id=attempt.id))

    test = Test.query.get_or_404(attempt.test_id)

    # جلب الأسئلة بترتيبها
    questions = TestQuestion.query.filter_by(test_id=test.id).order_by(TestQuestion.order).all()

    # جلب الإجابات مرتبة حسب السؤال
    answers = TestAnswer.query.filter_by(attempt_id=attempt.id).all()
    answers_by_question = {answer.question_id: answer for answer in answers}

    return render_template(
        'student/test_results.html',
        test=test,
        attempt=attempt,
        questions=questions,
        answers_by_question=answers_by_question
    )

@student_tests.route('/tests/history')
@login_required
def test_history():
    """عرض سجل محاولات الاختبارات للطالب"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))

    # جلب جميع محاولات الطالب المكتملة
    attempts = TestAttempt.query.filter_by(
        user_id=current_user.id, 
        completed_at=not None
    ).order_by(TestAttempt.completed_at.desc()).all()

    # تنظيم المحاولات حسب الاختبار
    attempts_by_test = {}
    for attempt in attempts:
        if attempt.test_id not in attempts_by_test:
            attempts_by_test[attempt.test_id] = []
        attempts_by_test[attempt.test_id].append(attempt)

    # جلب الاختبارات التي تم محاولتها
    test_ids = [a.test_id for a in attempts]
    tests = Test.query.filter(Test.id.in_(test_ids)).all()
    tests_dict = {test.id: test for test in tests}

    return render_template(
        'student/test_history.html',
        attempts=attempts,
        attempts_by_test=attempts_by_test,
        tests=tests_dict
    )
@admin_tests.route('/admin/tests/create_manual', methods=['GET', 'POST'])
@login_required
def create_manual_test():
    """إنشاء اختبار يدوي جديد مع إضافة الأسئلة مباشرة"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    form = TestForm()

    if form.validate_on_submit():
        test = Test(
            title=form.title.data,
            description=form.description.data,
            created_by=current_user.id,
            time_limit_minutes=form.time_limit_minutes.data,
            passing_score=form.passing_score.data,
            is_active=form.is_active.data
        )
        db.session.add(test)
        db.session.commit()

        # معالجة الأسئلة المضافة يدويًا
        questions_data = request.form.to_dict(flat=False)

        # الحصول على عدد الأسئلة المقدمة من خلال البيانات
        question_indices = set()
        for key in questions_data.keys():
            if key.startswith('questions[') and key.endswith('][text]'):
                index = key.split('[')[1].split(']')[0]
                question_indices.add(index)

        # إنشاء كل سؤال
        for index in question_indices:
            question_text = questions_data.get(f'questions[{index}][text]', [''])[0]
            question_type = questions_data.get(f'questions[{index}][type]', ['multiple_choice'])[0]
            points = int(questions_data.get(f'questions[{index}][points]', ['1'])[0])

            if not question_text:
                continue

            # إنشاء السؤال
            question = TestQuestion(
                test_id=test.id,
                question_text=question_text,
                question_type=question_type,
                points=points,
                order=int(index) + 1
            )
            db.session.add(question)
            db.session.flush()  # للحصول على معرف السؤال

            # إضافة الخيارات إذا كان السؤال اختيار من متعدد أو صح/خطأ
            if question_type in ['multiple_choice', 'true_false']:
                choices = []
                correct_index = int(questions_data.get(f'questions[{index}][correct]', ['0'])[0])

                for choice_index in range(4):  # نفترض حد أقصى 4 خيارات
                    choice_key = f'questions[{index}][choices][{choice_index}]'
                    if choice_key in questions_data and questions_data[choice_key][0]:
                        choice = QuestionChoice(
                            question_id=question.id,
                            choice_text=questions_data[choice_key][0],
                            is_correct=(choice_index == correct_index),
                            order=choice_index + 1
                        )
                        db.session.add(choice)

        db.session.commit()
        flash('تم إنشاء الاختبار والأسئلة بنجاح.', 'success')
        return redirect(url_for('admin_tests.manage_tests'))

    return render_template('admin/create_manual_test.html', form=form)