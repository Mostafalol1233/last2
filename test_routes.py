"""
هذا الملف يحتوي على routes الخاصة بالاختبارات سواء للمسؤول أو للطلاب
"""

import os
import re
import tempfile
import io
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

# استيراد مكتبات معالجة الملفات
from pypdf import PdfReader
import docx

from app import db, app
from models import Test, TestQuestion, QuestionChoice, TestAttempt, TestAnswer, TestRetryRequest, User
from forms import (
    TestCreateForm as TestForm, 
    TestQuestionForm, 
    QuestionChoiceForm, 
    TestAnswerForm, 
    TestAttemptForm, 
    TestTakingForm,
    TestRetryRequestForm,
    TestRetryResponseForm
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

@admin_tests.route('/admin/retry_requests')
@login_required
def retry_requests():
    """عرض طلبات المحاولة الإضافية للاختبارات"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    # جلب جميع طلبات المحاولة الإضافية مع بيانات الاختبار والطالب
    pending_requests = TestRetryRequest.query.filter_by(status='pending').order_by(TestRetryRequest.request_date.desc()).all()
    responded_requests = TestRetryRequest.query.filter(TestRetryRequest.status != 'pending').order_by(TestRetryRequest.response_date.desc()).limit(20).all()
    
    return render_template(
        'admin/retry_requests.html',
        pending_requests=pending_requests,
        responded_requests=responded_requests
    )

@admin_tests.route('/admin/retry_requests/<int:request_id>/respond', methods=['GET', 'POST'])
@login_required
def respond_retry_request(request_id):
    """الرد على طلب محاولة إضافية للاختبار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    retry_request = TestRetryRequest.query.get_or_404(request_id)
    
    # التحقق من حالة الطلب
    if retry_request.status != 'pending':
        flash('تم الرد على هذا الطلب بالفعل.', 'info')
        return redirect(url_for('admin_tests.retry_requests'))
    
    # جلب معلومات الاختبار والطالب
    test = Test.query.get_or_404(retry_request.test_id)
    student = User.query.get_or_404(retry_request.user_id)
    
    form = TestRetryResponseForm()
    form.request_id.data = request_id
    
    if form.validate_on_submit():
        # تحديث حالة الطلب
        retry_request.status = form.status.data
        retry_request.admin_response = form.admin_response.data
        retry_request.response_date = datetime.utcnow()
        retry_request.responded_by = current_user.id
        
        db.session.commit()
        
        flash('تم الرد على طلب المحاولة الإضافية بنجاح.', 'success')
        return redirect(url_for('admin_tests.retry_requests'))
    
    return render_template(
        'admin/respond_retry_request.html',
        retry_request=retry_request,
        test=test,
        student=student,
        form=form
    )

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
            is_active=form.is_active.data,
            # إضافة خيارات الوصول للاختبار
            access_type=form.access_type.data,
            points_required=form.points_required.data if form.access_type.data == 'points' else 0,
            access_code=form.access_code.data if form.access_type.data == 'code' else None
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
        # تحديث الحقول الأساسية
        test.title = form.title.data
        test.description = form.description.data
        test.time_limit_minutes = form.time_limit_minutes.data
        test.passing_score = form.passing_score.data
        test.max_attempts = form.max_attempts.data
        test.is_active = form.is_active.data
        
        # تحديث خيارات الوصول
        test.access_type = form.access_type.data
        test.points_required = form.points_required.data if form.access_type.data == 'points' else 0
        test.access_code = form.access_code.data if form.access_type.data == 'code' else None
        
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
        
        # إنشاء السؤال
        question = TestQuestion(
            test_id=test.id,
            question_text=form.question_text.data,
            question_type=form.question_type.data,
            points=form.points.data,
            order=next_order
        )
        
        # حفظ الصورة إذا تم تحميلها
        if form.question_image.data:
            # التأكد من وجود مجلد للصور
            tests_img_path = os.path.join(app.static_folder, 'img', 'tests')
            os.makedirs(tests_img_path, exist_ok=True)
            
            # تأمين اسم الملف وحفظه
            filename = secure_filename(form.question_image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"question_{timestamp}_{filename}"
            image_path = os.path.join(tests_img_path, image_filename)
            
            # حفظ الملف
            form.question_image.data.save(image_path)
            
            # تخزين مسار الصورة في قاعدة البيانات (مسار نسبي من مجلد static)
            question.image_path = f"img/tests/{image_filename}"
            
            logging.info(f"تم حفظ صورة للسؤال في المسار: {question.image_path}")
        
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
        # نحتفظ بالقيم القديمة قبل تحديثها عبر النموذج
        old_image_path = question.image_path
        
        # تحديث جميع حقول السؤال من النموذج باستثناء صورة السؤال (لأنها حقل خاص)
        form.populate_obj(question)
        
        # التعامل مع صورة السؤال إذا تم تحميلها
        if form.question_image.data:
            # التأكد من وجود مجلد للصور
            tests_img_path = os.path.join(app.static_folder, 'img', 'tests')
            os.makedirs(tests_img_path, exist_ok=True)
            
            # تأمين اسم الملف وحفظه
            filename = secure_filename(form.question_image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"question_{timestamp}_{filename}"
            image_path = os.path.join(tests_img_path, image_filename)
            
            # حفظ الملف
            form.question_image.data.save(image_path)
            
            # تخزين مسار الصورة في قاعدة البيانات (مسار نسبي من مجلد static)
            question.image_path = f"img/tests/{image_filename}"
            
            logging.info(f"تم تحديث صورة السؤال في المسار: {question.image_path}")
        
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
def admin_test_results(test_id):
    """عرض نتائج الاختبار للمسؤول مع إمكانية تفعيل/إلغاء تفعيل الاختبار"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    test = Test.query.get_or_404(test_id)
    
    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لعرض نتائج هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))
    
    # جلب محاولة محددة إذا تم تحديدها في الاستعلام
    attempt_id = request.args.get('attempt_id', type=int)
    
    if attempt_id:
        # عرض نتائج محاولة محددة (بالتفصيل)
        attempt = TestAttempt.query.get_or_404(attempt_id)
        
        # التحقق من أن هذه المحاولة تنتمي للاختبار المطلوب
        if attempt.test_id != int(test_id):
            flash('المحاولة المطلوبة غير موجودة في هذا الاختبار', 'danger')
            return redirect(url_for('admin_tests.admin_test_results', test_id=test_id))
        
        # التحقق من اكتمال المحاولة
        if not attempt.completed_at:
            flash('هذه المحاولة غير مكتملة بعد', 'danger')
            return redirect(url_for('admin_tests.admin_test_results', test_id=test_id))
        
        # جلب الطالب الذي قام بالمحاولة
        student = User.query.get_or_404(attempt.user_id)
        
        # جلب الأسئلة بترتيبها
        questions = TestQuestion.query.filter_by(test_id=test.id).order_by(TestQuestion.order).all()
        
        # جلب الإجابات مرتبة حسب السؤال
        answers = TestAnswer.query.filter_by(attempt_id=attempt.id).all()
        answers_by_question = {answer.question_id: answer for answer in answers}
        
        # تسجيل معلومات للتصحيح
        logging.info(f"المسؤول {current_user.username} يعرض نتائج الاختبار: {test.title}")
        logging.info(f"معرف المحاولة: {attempt_id}, الطالب: {student.username}")
        logging.info(f"حالة الاختبار: {'مفعل' if test.is_active else 'غير مفعل'}")
        logging.info(f"عدد الأسئلة: {len(questions)}, عدد الإجابات: {len(answers)}")
        
        return render_template(
            'admin/test_results.html',
            test=test,
            attempt=attempt,
            student=student,
            questions=questions,
            answers=answers,
            answers_by_question=answers_by_question,
            show_toggle_controls=True  # إظهار أزرار التحكم في حالة الاختبار
        )
    else:
        # عرض قائمة المحاولات للاختبار
        # جلب جميع محاولات الاختبار المكتملة مرتبة بالتاريخ
        attempts = TestAttempt.query.filter_by(test_id=test_id, completed_at=not None).order_by(TestAttempt.completed_at.desc()).all()
        
        # حساب إحصائيات الاختبار
        total_attempts = len(attempts)
        passed_attempts = sum(1 for a in attempts if a.passed)
        average_score = sum(a.score for a in attempts) / total_attempts if total_attempts > 0 else 0
        
        # إضافة معلومات الطالب لكل محاولة
        for attempt in attempts:
            attempt.student = User.query.get(attempt.user_id)
        
        return render_template(
            'admin/test_results_list.html',
            test=test,
            attempts=attempts,
            total_attempts=total_attempts,
            passed_attempts=passed_attempts,
            average_score=average_score
        )

#################
# Student Routes #
#################

@student_tests.route('/')
@login_required
def available_tests():
    """عرض الاختبارات المتاحة للطالب"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط. استخدم واجهة الإدارة للوصول إلى الاختبارات.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    # تسجيل الدخول للتصحيح
    logging.info(f"الطالب {current_user.username} يعرض الاختبارات المتاحة")
    
    # الاختبارات النشطة فقط
    tests = Test.query.filter_by(is_active=True).all()
    
    # جلب طلبات المحاولات الإضافية المعتمدة
    approved_retry_requests = TestRetryRequest.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()
    approved_retry_test_ids = [r.test_id for r in approved_retry_requests]
    
    # جلب محاولات الطالب لكل اختبار
    all_attempts = TestAttempt.query.filter_by(user_id=current_user.id).all()
    
    # تنظيم المحاولات حسب الاختبار
    attempts_by_test = {}
    for attempt in all_attempts:
        if attempt.test_id not in attempts_by_test:
            attempts_by_test[attempt.test_id] = []
        attempts_by_test[attempt.test_id].append(attempt)
    
    # جمع إحصائيات حول حالة كل اختبار بالنسبة للطالب
    test_status = {}
    for test in tests:
        test_attempts = attempts_by_test.get(test.id, [])
        completed_attempts = [a for a in test_attempts if a.completed_at is not None]
        pending_attempts = [a for a in test_attempts if a.completed_at is None]
        
        # تسجيل للتصحيح
        logging.info(f"اختبار {test.id}: {test.title}")
        logging.info(f"  - إجمالي المحاولات: {len(test_attempts)}")
        logging.info(f"  - المحاولات المكتملة: {len(completed_attempts)}")
        logging.info(f"  - المحاولات المعلقة: {len(pending_attempts)}")
        logging.info(f"  - الحد الأقصى للمحاولات المسموح بها: {test.max_attempts}")
        
        # أفضل نتيجة
        best_score = 0
        if completed_attempts:
            scores = [a.score for a in completed_attempts if a.score is not None]
            best_score = max(scores) if scores else 0
            
        # عدد المحاولات الناجحة
        passed_attempts = [a for a in completed_attempts if a.passed]
        
        # التحقق من وجود طلب محاولة إضافية معتمد
        has_approved_retry = test.id in approved_retry_test_ids
        
        # المحاولات المتبقية
        remaining_attempts = test.max_attempts - len(completed_attempts)
        if has_approved_retry:
            remaining_attempts += 1
            
        # تسجيل المحاولات المتبقية للتصحيح
        logging.info(f"  - المحاولات المتبقية: {remaining_attempts}")
        
        test_status[test.id] = {
            'completed_count': len(completed_attempts),
            'pending_count': len(pending_attempts),
            'best_score': best_score,
            'passed_count': len(passed_attempts),
            'remaining_attempts': max(0, remaining_attempts),
            'has_approved_retry': has_approved_retry,
            'max_attempts': test.max_attempts
        }
    
    # المحاولات المكتملة فقط للعرض في جدول السجل - مرتبة من الأحدث إلى الأقدم
    completed_attempts = [a for a in all_attempts if a.completed_at is not None]
    completed_attempts.sort(key=lambda x: x.completed_at, reverse=True)
    
    return render_template(
        'student/tests.html',
        active_tests=tests,
        attempts=all_attempts,
        attempts_by_test=attempts_by_test,
        completed_attempts=completed_attempts[:10],  # آخر 10 محاولات مكتملة فقط
        test_status=test_status
    )

@student_tests.route('/<int:test_id>/start', methods=['GET', 'POST'])
@login_required
def start_test(test_id):
    """بدء اختبار جديد"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    test = Test.query.get_or_404(test_id)
    logging.info(f"الطالب {current_user.username} يحاول بدء اختبار {test.id}: {test.title}")
    logging.info(f"الحد الأقصى للمحاولات لهذا الاختبار: {test.max_attempts}")
    logging.info(f"نوع الوصول للاختبار: {test.access_type}")
    
    # التحقق من أن الاختبار نشط
    if not test.is_active:
        flash('هذا الاختبار غير متاح حاليًا.', 'warning')
        return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من نوع الوصول للاختبار
    if test.access_type == 'points':
        # التحقق من امتلاك الطالب نقاط كافية
        if current_user.points < test.points_required:
            flash(f'لا يمكنك الوصول لهذا الاختبار. أنت بحاجة إلى {test.points_required} نقطة، ولديك فقط {current_user.points} نقطة.', 'danger')
            return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من كود الوصول إذا كان الاختبار يتطلب ذلك
    if test.access_type == 'code':
        # إذا كان الوصول بكود ولم يتم توفير كود في النموذج
        access_code = request.form.get('access_code')
        if not access_code:
            flash('هذا الاختبار يتطلب كود وصول.', 'warning')
            return redirect(url_for('student_tests.available_tests'))
        
        # التحقق من صحة الكود
        if access_code != test.access_code:
            flash('كود الوصول غير صحيح.', 'danger')
            return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من وجود محاولة غير مكتملة للطالب
    existing_attempt = TestAttempt.query.filter_by(
        test_id=test_id, 
        user_id=current_user.id, 
        completed_at=None
    ).first()
    
    if existing_attempt:
        # استئناف المحاولة الموجودة
        logging.info(f"وجدت محاولة غير مكتملة للطالب {current_user.username} للاختبار {test_id} - معرف المحاولة: {existing_attempt.id}")
        flash('لديك محاولة غير مكتملة لهذا الاختبار. سيتم استئنافها الآن.', 'info')
        return redirect(url_for('student_tests.take_test', attempt_id=existing_attempt.id))
    
    # التحقق من وجود محاولة سابقة مكتملة لهذا الاختبار
    completed_attempts = TestAttempt.query.filter_by(
        test_id=test_id,
        user_id=current_user.id
    ).filter(TestAttempt.completed_at.isnot(None)).all()
    
    # نحسب عدد المحاولات المكتملة
    completed_attempts_count = len(completed_attempts)
    logging.info(f"عدد المحاولات المكتملة للطالب {current_user.username} للاختبار {test_id}: {completed_attempts_count}")
    
    # التحقق من أن الطلب نوعه POST (من الزر في الصفحة) وليس GET (من URL مباشرة)
    if request.method != 'POST':
        # إعادة توجيه إلى صفحة الاختبارات المتاحة إذا كانت الطريقة GET
        logging.info(f"محاولة وصول مباشر (GET) من الطالب {current_user.username} إلى اختبار {test_id} - تم إعادة التوجيه")
        return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من وجود طلب محاولة إضافية معتمد للطالب
    approved_retry_request = TestRetryRequest.query.filter_by(
        test_id=test_id,
        user_id=current_user.id,
        status='approved'
    ).first()
    
    # التحقق من عدم وجود محاولة سابقة تم استخدامها (لأن المشرف قد أعطى محاولة إضافية)
    has_used_retry = TestRetryRequest.query.filter_by(
        test_id=test_id,
        user_id=current_user.id,
        status='used'
    ).first()
    
    if approved_retry_request:
        logging.info(f"وجدت طلب محاولة إضافية معتمد للطالب {current_user.username} للاختبار {test_id}")
    
    # التحقق من عدد المحاولات المسموح بها وطلبات المحاولة الإضافية
    if completed_attempts_count >= test.max_attempts and not approved_retry_request and not has_used_retry:
        logging.warning(f"الطالب {current_user.username} حاول بدء اختبار {test_id} ولكنه استنفد الحد الأقصى للمحاولات ({test.max_attempts})")
        flash(f'لقد استنفذت الحد الأقصى لعدد المحاولات المسموح بها ({test.max_attempts}). يمكنك طلب محاولة إضافية من المشرف.', 'warning')
        return redirect(url_for('student_tests.request_retry', test_id=test_id))
    
    if completed_attempts_count > 0 and not approved_retry_request and not has_used_retry:
        remaining_attempts = test.max_attempts - completed_attempts_count
        logging.info(f"الطالب {current_user.username} لديه {remaining_attempts} محاولات متبقية للاختبار {test_id}")
        flash(f'لديك {remaining_attempts} محاولات متبقية لهذا الاختبار من أصل {test.max_attempts}.', 'info')
    
    # استخدام طلب المحاولة الإضافية إذا كان موجودًا (بتعيين حالته إلى "used")
    if approved_retry_request:
        logging.info(f"استخدام طلب المحاولة الإضافية المعتمد للطالب {current_user.username} للاختبار {test_id}")
        approved_retry_request.status = 'used'
        db.session.commit()
    
    # إنشاء محاولة جديدة
    attempt = TestAttempt(
        test_id=test_id,
        user_id=current_user.id,
        started_at=datetime.utcnow()
    )
    db.session.add(attempt)
    
    # خصم النقاط إذا كان الاختبار يتطلب ذلك
    if test.access_type == 'points':
        # تسجيل إضافي قبل خصم النقاط
        logging.info(f"قبل الخصم: الطالب {current_user.username} لديه {current_user.points} نقطة")
        logging.info(f"سيتم خصم {test.points_required} نقطة للوصول إلى الاختبار {test.title}")
        
        try:
            # خصم النقاط من رصيد المستخدم
            current_user.points -= test.points_required
            
            # التأكد من حفظ التغييرات
            db.session.commit()
            
            # تسجيل نجاح العملية
            logging.info(f"تم خصم {test.points_required} نقطة من رصيد الطالب {current_user.username}. الرصيد الجديد: {current_user.points}")
            flash(f'تم خصم {test.points_required} نقطة من رصيدك. رصيدك الحالي هو {current_user.points} نقطة.', 'info')
        except Exception as e:
            # تسجيل الخطأ إذا حدث
            logging.error(f"خطأ أثناء خصم النقاط: {str(e)}")
            db.session.rollback()
    else:
        # حفظ المحاولة الجديدة فقط إذا لم تكن هناك حاجة لخصم نقاط
        db.session.commit()
    logging.info(f"تم إنشاء محاولة جديدة للطالب {current_user.username} للاختبار {test_id} - معرف المحاولة: {attempt.id}")
    
    # إنشاء إجابات فارغة لجميع أسئلة الاختبار
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    for question in questions:
        answer = TestAnswer(
            attempt_id=attempt.id,
            question_id=question.id
        )
        db.session.add(answer)
    
    db.session.commit()
    logging.info(f"تم إنشاء {len(questions)} إجابات فارغة للمحاولة {attempt.id}")
    
    flash('تم بدء الاختبار. ستظهر لك الأسئلة الآن. أحسن استخدام وقت الاختبار!', 'info')
    return redirect(url_for('student_tests.take_test', attempt_id=attempt.id))

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
    
    # التأكد من وجود سجل إجابة لكل سؤال (هذا يضمن أن جميع الأسئلة لديها سجلات إجابات)
    for question in questions:
        if question.id not in answers:
            new_answer = TestAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_choice_id=None,
                text_answer=None,
                is_correct=False
            )
            db.session.add(new_answer)
            answers[question.id] = new_answer
    
    db.session.commit()  # حفظ الإجابات الجديدة
    
    # معالجة تسليم النموذج
    if request.method == 'POST':
        action = request.form.get('action', 'save')
        
        # حفظ الإجابات
        for question in questions:
            answer_value = request.form.get(f'question_{question.id}')
            answer = answers.get(question.id)
            
            if answer and answer_value:
                if question.question_type in ['multiple_choice', 'true_false']:
                    try:
                        choice = QuestionChoice.query.get(int(answer_value))
                        if choice:
                            answer.selected_choice_id = choice.id
                            answer.is_correct = choice.is_correct
                            # إضافة تسجيل لأغراض التصحيح
                            logging.info(f"Saved answer for question {question.id}, choice {choice.id}, is_correct: {choice.is_correct}")
                    except (ValueError, TypeError) as e:
                        # تسجيل الخطأ ولكن لا تتوقف العملية
                        logging.error(f"Error saving choice answer: {str(e)}")
                elif question.question_type == 'short_answer':
                    answer.text_answer = answer_value
                    answer.is_correct = grade_short_answer(question, answer_value)
                    logging.info(f"Saved short answer for question {question.id}: {answer_value}")
        
        # تأكد من حفظ التغييرات
        try:
            db.session.commit()
            logging.info("Successfully saved all answers")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error committing answers: {str(e)}")
            flash('حدث خطأ أثناء حفظ إجاباتك. يرجى المحاولة مرة أخرى.', 'danger')
            return redirect(url_for('student_tests.take_test', attempt_id=attempt.id))
        
        # إذا كان طلب AJAX (الحفظ التلقائي)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'تم حفظ الإجابات'})
        
        if action == 'submit':
            # إكمال الاختبار
            attempt.completed_at = datetime.utcnow()
            
            # تأكد من حساب النتيجة بشكل صحيح
            try:
                attempt.score = attempt.calculate_score()
                attempt.passed = attempt.score >= test.passing_score
                logging.info(f"Test submitted. Score: {attempt.score}, Passing score: {test.passing_score}, Passed: {attempt.passed}")
                
                db.session.commit()
                flash('تم تسليم الاختبار بنجاح. يمكنك الآن عرض نتائجك.', 'success')
                return redirect(url_for('student_tests.test_results', attempt_id=attempt.id))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error calculating score or submitting test: {str(e)}")
                flash('حدث خطأ أثناء تسليم الاختبار. يرجى المحاولة مرة أخرى.', 'danger')
                return redirect(url_for('student_tests.take_test', attempt_id=attempt.id))
        
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
    """عرض نتائج محاولة اختبار للطالب"""
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
    
    # تسجيل المعلومات للتصحيح
    logging.info(f"عرض نتائج الاختبار للطالب {current_user.username}")
    logging.info(f"معرف المحاولة: {attempt_id}, نتيجة: {attempt.score}%, اجتياز: {attempt.passed}")
    logging.info(f"حالة الاختبار: {'مفعل' if test.is_active else 'غير مفعل'}")
    logging.info(f"عدد الأسئلة: {len(questions)}, عدد الإجابات: {len(answers)}")
    
    # التأكد من أن كل سؤال له خيارات مرتبطة به إذا كان من نوع متعدد الاختيارات
    for question in questions:
        if question.question_type in ['multiple_choice', 'true_false']:
            choices_count = len(question.choices.all()) if hasattr(question, 'choices') else 0
            logging.info(f"السؤال {question.id}: نوعه {question.question_type}، عدد الخيارات: {choices_count}")
    
    # حساب عدد المحاولات المكتملة للاختبار
    all_attempts = TestAttempt.query.filter_by(
        test_id=test.id,
        user_id=current_user.id
    ).all()
    
    # تنظيم المحاولات حسب الحالة
    attempt_counts = {
        'completed': len([a for a in all_attempts if a.completed_at is not None]),
        'pending': len([a for a in all_attempts if a.completed_at is None])
    }
    
    # حساب المحاولات المتبقية
    completed_attempts_count = attempt_counts['completed']
    remaining_attempts = max(0, test.max_attempts - completed_attempts_count)
    
    # طلبات المحاولة الإضافية المعتمدة
    approved_retry_request = TestRetryRequest.query.filter_by(
        test_id=test.id,
        user_id=current_user.id,
        status='approved'
    ).first()
    
    if approved_retry_request:
        remaining_attempts += 1
    
    # تمرير معلومات حالة الاختبار (مفعل أم لا) للقالب
    # عندما يكون الاختبار غير مفعل، يمكن للطلاب رؤية الإجابات الصحيحة والخاطئة
    return render_template(
        'student/test_results.html',
        test=test,
        attempt=attempt,
        questions=questions,
        answers=answers,
        answers_by_question=answers_by_question,
        attempt_counts=attempt_counts,
        remaining_attempts=remaining_attempts,
        show_answers=not test.is_active  # إظهار الإجابات للطلاب فقط عندما يكون الاختبار غير مفعل
    )

@student_tests.route('/history')
@login_required
def test_history():
    """عرض سجل محاولات الاختبارات للطالب"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    # سجل دخول المستخدم للصفحة
    logging.info(f"الطالب {current_user.username} يعرض سجل الاختبارات")
    
    # جلب جميع محاولات الطالب المكتملة
    attempts = TestAttempt.query.filter_by(
        user_id=current_user.id
    ).filter(TestAttempt.completed_at.isnot(None)).order_by(TestAttempt.completed_at.desc()).all()
    
    # تسجيل عدد المحاولات المكتملة
    logging.info(f"عدد محاولات الاختبار المكتملة للطالب {current_user.username}: {len(attempts)}")
    
    # جلب طلبات المحاولات الإضافية المعتمدة والمستخدمة
    approved_retry_requests = {r.test_id: r for r in TestRetryRequest.query.filter(
        TestRetryRequest.user_id == current_user.id,
        TestRetryRequest.status.in_(['approved', 'used'])
    ).all()}
    
    # تنظيم المحاولات حسب الاختبار
    attempts_by_test = {}
    for attempt in attempts:
        if attempt.test_id not in attempts_by_test:
            attempts_by_test[attempt.test_id] = []
        attempts_by_test[attempt.test_id].append(attempt)
    
    # جلب الاختبارات التي تم محاولتها
    test_ids = list(set([a.test_id for a in attempts]))
    tests = Test.query.filter(Test.id.in_(test_ids)).all() if test_ids else []
    tests_dict = {test.id: test for test in tests}
    
    # تخزين معلومات الحالة لكل اختبار
    test_status = {}
    for test_id, test_attempts in attempts_by_test.items():
        if test_id not in tests_dict:
            continue
            
        test = tests_dict[test_id]
        passed_count = sum(1 for a in test_attempts if a.passed)
        best_score = max((a.score or 0) for a in test_attempts) if test_attempts else 0
        completed_count = len(test_attempts)
        
        # التحقق من طلبات محاولة إضافية معتمدة
        has_approved_retry = test_id in approved_retry_requests
        
        # حساب المحاولات المتبقية
        remaining_attempts = test.max_attempts - completed_count
        if has_approved_retry:
            remaining_attempts += 1  # إضافة محاولة إضافية إذا كان هناك طلب معتمد
        
        test_status[test_id] = {
            'completed_count': completed_count,
            'passed_count': passed_count,
            'best_score': best_score,
            'remaining_attempts': max(0, remaining_attempts),  # التأكد من أنها لا تقل عن صفر
            'has_approved_retry': has_approved_retry,
            'max_attempts': test.max_attempts
        }
        
        logging.info(f"الاختبار {test_id}: عدد المحاولات: {completed_count}/{test.max_attempts}, "
                    f"النجاح: {passed_count}, أفضل نتيجة: {best_score}%, "
                    f"المتبقي: {max(0, remaining_attempts)}")
    
    # تسجيل عدد الاختبارات التي تم محاولتها
    logging.info(f"عدد الاختبارات المختلفة التي حاولها الطالب {current_user.username}: {len(tests_dict)}")
    
    # جلب جميع طلبات المحاولات الإضافية
    retry_requests = TestRetryRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(TestRetryRequest.request_date.desc()).all()
    
    return render_template(
        'student/test_history.html',
        attempts=attempts,
        attempts_by_test=attempts_by_test,
        tests=tests_dict,
        retry_requests=retry_requests,
        test_status=test_status  # إرسال معلومات الحالة الإضافية
    )
    
@student_tests.route('/<int:test_id>/request_retry', methods=['GET', 'POST'])
@login_required
def request_retry(test_id):
    """طلب محاولة إضافية للاختبار"""
    if current_user.is_admin():
        flash('هذه الصفحة مخصصة للطلاب فقط.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    test = Test.query.get_or_404(test_id)
    
    # جلب جميع المحاولات المكتملة للطالب في هذا الاختبار
    completed_attempts = TestAttempt.query.filter_by(
        test_id=test_id,
        user_id=current_user.id
    ).filter(TestAttempt.completed_at.isnot(None)).all()
    
    completed_attempts_count = len(completed_attempts)
    if completed_attempts_count == 0:
        flash('لم تقم بإجراء هذا الاختبار بعد. يجب عليك إكمال الاختبار أولاً قبل طلب محاولة إضافية.', 'warning')
        return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من أن الطالب قد استنفد الحد الأقصى من المحاولات المسموح بها
    if completed_attempts_count < test.max_attempts:
        remaining_attempts = test.max_attempts - completed_attempts_count
        flash(f'لا يمكنك طلب محاولة إضافية لأنك لم تستنفد عدد المحاولات المسموح بها بعد. لديك {remaining_attempts} محاولات متبقية.', 'warning')
        return redirect(url_for('student_tests.available_tests'))
    
    # التحقق من وجود طلب قيد الانتظار
    pending_request = TestRetryRequest.query.filter_by(
        test_id=test_id,
        user_id=current_user.id,
        status='pending'
    ).first()
    
    if pending_request:
        flash('لديك بالفعل طلب محاولة إضافية قيد الانتظار لهذا الاختبار.', 'info')
        return redirect(url_for('student_tests.test_history'))
    
    # التحقق من وجود طلب معتمد أو تم استخدامه
    approved_request = TestRetryRequest.query.filter(
        TestRetryRequest.test_id == test_id,
        TestRetryRequest.user_id == current_user.id,
        TestRetryRequest.status.in_(['approved', 'used'])
    ).first()
    
    if approved_request:
        if approved_request.status == 'used':
            flash('لقد استخدمت بالفعل المحاولة الإضافية التي تمت الموافقة عليها لهذا الاختبار. يمكنك تقديم طلب جديد إذا كنت بحاجة إلى محاولة أخرى.', 'info')
            return redirect(url_for('student_tests.test_history'))
        else:
            flash('تمت الموافقة على طلب محاولة إضافية لهذا الاختبار بالفعل. يمكنك بدء الاختبار الآن.', 'success')
            return redirect(url_for('student_tests.start_test', test_id=test_id))
    
    form = TestRetryRequestForm()
    form.test_id.data = test_id
    
    if form.validate_on_submit():
        # إنشاء طلب محاولة إضافية
        retry_request = TestRetryRequest(
            test_id=test_id,
            user_id=current_user.id,
            reason=form.reason.data,
            request_date=datetime.utcnow(),
            status='pending'
        )
        db.session.add(retry_request)
        db.session.commit()
        
        # تسجيل بيانات الطلب
        logging.info(f"تم إنشاء طلب محاولة إضافية جديد: الطالب {current_user.username} للاختبار {test.title}, المعرف {retry_request.id}")
        
        flash('تم إرسال طلب المحاولة الإضافية بنجاح. سيتم إعلامك بالرد قريبًا.', 'success')
        return redirect(url_for('student_tests.test_history'))
    
    # جلب آخر محاولة للعرض في الطلب
    latest_attempt = TestAttempt.query.filter_by(
        test_id=test_id,
        user_id=current_user.id
    ).filter(TestAttempt.completed_at.isnot(None)).order_by(TestAttempt.completed_at.desc()).first()
    
    return render_template(
        'student/request_retry.html',
        test=test,
        form=form,
        completed_attempt=latest_attempt,
        completed_attempts_count=completed_attempts_count
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
                    choice_text = questions_data.get(choice_key, [''])[0]
                    
                    if choice_text:  # إضافة الخيار فقط إذا كان هناك نص له
                        is_correct = (choice_index == correct_index)
                        choices.append({
                            'text': choice_text,
                            'is_correct': is_correct
                        })
                
                # إنشاء خيارات السؤال
                for choice_data in choices:
                    choice = QuestionChoice(
                        question=question,
                        text=choice_data['text'],
                        is_correct=choice_data['is_correct']
                    )
                    db.session.add(choice)
            elif question_type == 'short_answer':
                # الأسئلة ذات الإجابة القصيرة تحتاج إلى إجابة نموذجية
                correct_answer = questions_data.get(f'questions[{index}][correct_answer]', [''])[0]
                question.correct_answer = correct_answer

@admin_tests.route('/admin/tests/<int:test_id>/toggle_status')
@login_required
def toggle_test_status(test_id):
    """تغيير حالة تفعيل الاختبار (تفعيل/إلغاء تفعيل)"""
    if not current_user.is_admin():
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    test = Test.query.get_or_404(test_id)
    
    # التحقق من أن المسؤول هو من أنشأ الاختبار
    if test.created_by != current_user.id:
        flash('ليس لديك صلاحية لتعديل هذا الاختبار', 'danger')
        return redirect(url_for('admin_tests.manage_tests'))
        
    # تغيير حالة التفعيل
    test.is_active = not test.is_active
    db.session.commit()
    
    # رسالة مناسبة
    if test.is_active:
        flash(f'تم تفعيل الاختبار "{test.title}" بنجاح.', 'success')
    else:
        flash(f'تم إلغاء تفعيل الاختبار "{test.title}" بنجاح. يمكن للطلاب الآن رؤية الإجابات الصحيحة.', 'success')
    
    return redirect(url_for('admin_tests.admin_test_results', test_id=test.id))


# وظيفة تقدير الإجابات القصيرة
def grade_short_answer(question, answer_text):
    """
    تقدير الإجابة القصيرة بناءً على الإجابة النموذجية المخزنة.
    في الوقت الحالي، نقوم بالمقارنة البسيطة مع الإجابة المخزنة.
    """
    if not answer_text:
        return False
        
    # TODO: تحسين هذه الوظيفة لتدعم تقديرات أكثر تعقيداً
    correct_answer = question.correct_answer
    if not correct_answer:
        # إذا لم تكن هناك إجابة نموذجية مخزنة، نعتبر الإجابة صحيحة إذا قدم الطالب أي شيء
        return bool(answer_text.strip())
    
    # مقارنة بسيطة (يمكن تحسينها لاحقاً)
    normalized_answer = answer_text.lower().strip()
    normalized_correct = correct_answer.lower().strip()
    
    return normalized_answer == normalized_correct