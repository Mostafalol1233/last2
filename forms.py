from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField, BooleanField, IntegerField, SelectMultipleField, FloatField
from wtforms.validators import DataRequired, Length, URL, Optional, EqualTo, ValidationError, NumberRange, Email
from models import User

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    submit = SubmitField('تسجيل الدخول')

class VideoUploadForm(FlaskForm):
    title = StringField('عنوان الفيديو', validators=[DataRequired(), Length(min=3, max=100)])
    url = StringField('رابط الفيديو', validators=[Optional(), URL()])
    video_file = FileField('ملف الفيديو', validators=[
        Optional(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv'], 'المرجو رفع ملفات فيديو فقط')
    ])
    description = TextAreaField('الوصف', validators=[Optional(), Length(max=2000)])
    requires_code = BooleanField('يتطلب كود للمشاهدة', default=True)
    points_cost = IntegerField('سعر الفيديو بالنقاط', default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('رفع الفيديو')

class TransferPointsForm(FlaskForm):
    student_id = SelectField('الطالب', coerce=int, validators=[DataRequired(message='يجب اختيار الطالب')])
    points = IntegerField('عدد النقاط', validators=[
        DataRequired(message='يجب إدخال عدد النقاط'),
        NumberRange(min=1, message='يجب أن يكون عدد النقاط أكبر من صفر')
    ])
    submit = SubmitField('تحويل النقاط')

class AddPointsForm(FlaskForm):
    points = IntegerField('عدد النقاط', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('إضافة النقاط')

class VideoEditForm(FlaskForm):
    title = StringField('عنوان الفيديو', validators=[DataRequired(), Length(min=3, max=100)])
    url = StringField('رابط الفيديو', validators=[Optional(), URL()])
    description = TextAreaField('الوصف', validators=[Optional(), Length(max=2000)])
    requires_code = BooleanField('يتطلب كود للمشاهدة')
    points_cost = IntegerField('سعر الفيديو بالنقاط', default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('تحديث الفيديو')

class PostForm(FlaskForm):
    title = StringField('عنوان المنشور', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('محتوى المنشور', validators=[DataRequired(), Length(min=10, max=5000)])
    submit = SubmitField('إنشاء منشور')

class CommentForm(FlaskForm):
    comment_text = TextAreaField('التعليق', validators=[DataRequired(), Length(min=1, max=500)])
    video_id = HiddenField('معرف الفيديو', validators=[DataRequired()])
    submit = SubmitField('نشر التعليق')

class LectureCodeForm(FlaskForm):
    code = StringField('كود المحاضرة', validators=[DataRequired(), Length(min=4, max=20)])
    video_id = HiddenField('معرف الفيديو', validators=[DataRequired()])
    submit = SubmitField('الدخول للمحاضرة')

class GenerateCodeForm(FlaskForm):
    video_id = HiddenField('معرف الفيديو', validators=[DataRequired()])
    student_id = SelectField('إرسال الكود للطالب (اختياري)', coerce=int, validators=[Optional()])
    multiple_students = BooleanField('إرسال أكواد لأكثر من طالب', default=False)
    num_codes = IntegerField('عدد الأكواد للإنشاء', default=1, validators=[NumberRange(min=1, max=100, message='يجب أن يكون العدد بين 1 و 100')])
    generate_pdf = BooleanField('إنشاء ملف PDF للأكواد', default=True)
    selected_students = SelectMultipleField('تحديد الطلاب (اختياري - لإرسال الأكواد لطلاب محددين)', coerce=int, validators=[Optional()])
    submit = SubmitField('توليد كود جديد')

class StudentNoteForm(FlaskForm):
    title = StringField('عنوان الملاحظة', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('محتوى الملاحظة', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('حفظ الملاحظة')

class AIChatForm(FlaskForm):
    message = TextAreaField('سؤالك', validators=[DataRequired(), Length(min=3, max=1000)])
    submit = SubmitField('إرسال')

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='يجب إدخال اسم المستخدم'),
        Length(min=3, max=64, message='يجب أن يكون اسم المستخدم بين 3 و 64 حرفاً')
    ])
    full_name = StringField('الاسم الثلاثي', validators=[
        DataRequired(message='يجب إدخال الاسم الثلاثي'),
        Length(min=5, max=100, message='يجب أن يكون الاسم الثلاثي بين 5 و 100 حرف')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        Optional(),
        Length(max=100, message='يجب أن لا يتجاوز البريد الإلكتروني 100 حرف'),
        Email(message='يرجى إدخال بريد إلكتروني صحيح')
    ])
    phone = StringField('رقم الهاتف', validators=[
        Optional(),
        Length(max=20, message='يجب أن لا يتجاوز رقم الهاتف 20 رقماً')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='يجب إدخال كلمة المرور'),
        Length(min=6, message='يجب أن تكون كلمة المرور 6 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يجب تأكيد كلمة المرور'),
        EqualTo('password', message='كلمة المرور غير متطابقة')
    ])
    role = SelectField('نوع الحساب', choices=[('student', 'طالب')], validators=[
        DataRequired(message='يجب اختيار نوع الحساب')
    ])
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError('يجب أن يحتوي اسم المستخدم على أحرف وأرقام فقط')
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('هذا الاسم مستخدم بالفعل، يرجى اختيار اسم آخر')

class ForgotPasswordForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='يجب إدخال اسم المستخدم'),
        Length(min=3, max=64, message='يجب أن يكون اسم المستخدم بين 3 و 64 حرفاً')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='يجب إدخال البريد الإلكتروني')
    ])
    phone = StringField('رقم الهاتف', validators=[
        DataRequired(message='يجب إدخال رقم الهاتف')
    ])
    submit = SubmitField('استعادة كلمة المرور')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('كلمة المرور الجديدة', validators=[
        DataRequired(message='يجب إدخال كلمة المرور'),
        Length(min=6, message='يجب أن تكون كلمة المرور 6 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يجب تأكيد كلمة المرور'),
        EqualTo('password', message='كلمة المرور غير متطابقة')
    ])
    submit = SubmitField('تغيير كلمة المرور')

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الثلاثي', validators=[
        DataRequired(message='يجب إدخال الاسم الثلاثي'),
        Length(min=5, max=100, message='يجب أن يكون الاسم الثلاثي بين 5 و 100 حرف')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        Optional(),
        Length(max=100, message='يجب أن لا يتجاوز البريد الإلكتروني 100 حرف')
    ])
    phone = StringField('رقم الهاتف', validators=[
        Optional(),
        Length(max=20, message='يجب أن لا يتجاوز رقم الهاتف 20 رقماً')
    ])
    submit = SubmitField('تحديث البيانات')

class DirectMessageForm(FlaskForm):
    recipient_id = SelectField('إرسال إلى', coerce=int, validators=[DataRequired(message='يجب اختيار المستلم')])
    message = TextAreaField('الرسالة', validators=[
        DataRequired(message='يجب كتابة نص الرسالة'),
        Length(min=1, max=1000, message='يجب أن تكون الرسالة بين 1 و 1000 حرف')
    ])
    submit = SubmitField('إرسال')

class PaymentForm(FlaskForm):
    """Form for creating/editing payment plans"""
    name = StringField('اسم الخطة', validators=[
        DataRequired(message='يجب إدخال اسم الخطة'),
        Length(min=3, max=100, message='يجب أن يكون اسم الخطة بين 3 و 100 حرف')
    ])
    description = TextAreaField('الوصف', validators=[
        Optional(),
        Length(max=500, message='يجب أن لا يتجاوز الوصف 500 حرف')
    ])
    price = FloatField('السعر', validators=[
        DataRequired(message='يجب إدخال السعر'),
        NumberRange(min=0, message='يجب أن يكون السعر قيمة موجبة')
    ])
    currency = SelectField('العملة', choices=[
        ('SAR', 'ريال سعودي'),
        ('USD', 'دولار أمريكي'),
        ('EUR', 'يورو')
    ], validators=[DataRequired(message='يجب اختيار العملة')])
    duration_days = IntegerField('مدة الاشتراك (بالأيام)', validators=[
        DataRequired(message='يجب إدخال مدة الاشتراك'),
        NumberRange(min=1, message='يجب أن تكون مدة الاشتراك يوم واحد على الأقل')
    ])
    features = TextAreaField('المميزات (ميزة واحدة في كل سطر)', validators=[
        Optional()
    ])
    submit = SubmitField('حفظ')

class SubscriptionSelectForm(FlaskForm):
    """Form for selecting subscription plan"""
    plan_id = SelectField('خطة الاشتراك', coerce=int, validators=[
        DataRequired(message='يجب اختيار خطة اشتراك')
    ])
    submit = SubmitField('اشتراك')

class SMSSettingsForm(FlaskForm):
    """Form for configuring SMS settings"""
    account_sid = StringField('Twilio Account SID', validators=[
        DataRequired(message='يجب إدخال Twilio Account SID')
    ])
    auth_token = PasswordField('Twilio Auth Token', validators=[
        DataRequired(message='يجب إدخال Twilio Auth Token')
    ])
    phone_number = StringField('رقم الهاتف', validators=[
        DataRequired(message='يجب إدخال رقم الهاتف'),
        Length(max=20, message='يجب أن لا يتجاوز رقم الهاتف 20 رقماً')
    ])
    submit = SubmitField('حفظ الإعدادات')

class SMSTestForm(FlaskForm):
    """Form for testing SMS functionality"""
    phone_number = StringField('رقم الهاتف للاختبار', validators=[
        DataRequired(message='يجب إدخال رقم الهاتف'),
        Length(max=20, message='يجب أن لا يتجاوز رقم الهاتف 20 رقماً')
    ])
    message = TextAreaField('نص الرسالة', validators=[
        DataRequired(message='يجب كتابة نص الرسالة'),
        Length(max=160, message='يجب أن لا يتجاوز طول الرسالة 160 حرفاً')
    ])
    submit = SubmitField('إرسال رسالة اختبار')

class BulkSMSForm(FlaskForm):
    """Form for sending bulk SMS messages"""
    user_ids = SelectMultipleField('تحديد المستخدمين', coerce=int, validators=[
        DataRequired(message='يجب تحديد مستخدم واحد على الأقل')
    ])
    message = TextAreaField('نص الرسالة', validators=[
        DataRequired(message='يجب كتابة نص الرسالة'),
        Length(max=160, message='يجب أن لا يتجاوز طول الرسالة 160 حرفاً')
    ])
    submit = SubmitField('إرسال الرسائل')

class TestCreateForm(FlaskForm):
    """Form for creating a new test"""
    title = StringField('عنوان الاختبار', validators=[
        DataRequired(message='يجب إدخال عنوان الاختبار'),
        Length(min=3, max=100, message='يجب أن يكون العنوان بين 3 و 100 حرف')
    ])
    description = TextAreaField('وصف الاختبار', validators=[
        Optional(),
        Length(max=500, message='يجب أن لا يتجاوز الوصف 500 حرف')
    ])
    test_file = FileField('ملف الاختبار (PDF/Word)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'يرجى رفع ملف بصيغة PDF أو Word فقط')
    ])
    time_limit_minutes = IntegerField('الوقت المحدد (بالدقائق)', validators=[
        DataRequired(message='يجب تحديد المدة الزمنية للاختبار'),
        NumberRange(min=5, max=180, message='يجب أن تكون المدة بين 5 و 180 دقيقة')
    ], default=30)
    passing_score = IntegerField('نسبة النجاح المطلوبة (%)', validators=[
        DataRequired(message='يجب تحديد نسبة النجاح'),
        NumberRange(min=50, max=100, message='يجب أن تكون النسبة بين 50% و 100%')
    ], default=60)
    max_attempts = IntegerField('الحد الأقصى لعدد المحاولات', validators=[
        DataRequired(message='يجب تحديد عدد المحاولات المسموح بها'),
        NumberRange(min=1, max=10, message='يجب أن يكون عدد المحاولات بين 1 و 10')
    ], default=1)
    is_active = BooleanField('نشط', default=True)
    # خيارات الوصول للاختبار
    access_type = SelectField('نوع الوصول للاختبار', choices=[
        ('free', 'مجاني للجميع'),
        ('points', 'يتطلب نقاط'),
        ('code', 'يتطلب كود خاص')
    ], default='free', validators=[DataRequired(message='يرجى اختيار نوع الوصول للاختبار')])
    points_required = IntegerField('عدد النقاط المطلوبة', validators=[
        Optional(),
        NumberRange(min=0, message='يجب أن تكون النقاط المطلوبة قيمة موجبة')
    ], default=0)
    access_code = StringField('كود الوصول للاختبار', validators=[
        Optional(),
        Length(min=4, max=20, message='يجب أن يكون الكود بين 4 و 20 حرفًا')
    ])
    submit = SubmitField('إنشاء الاختبار')

class TestQuestionForm(FlaskForm):
    """Form for adding a question to a test"""
    question_text = TextAreaField('السؤال', validators=[
        DataRequired(message='يجب إدخال نص السؤال'),
        Length(min=5, max=500, message='يجب أن يكون السؤال بين 5 و 500 حرف')
    ])
    question_type = SelectField('نوع السؤال', choices=[
        ('multiple_choice', 'اختيار من متعدد'),
        ('true_false', 'صح أو خطأ'),
        ('short_answer', 'إجابة قصيرة')
    ], validators=[DataRequired(message='يجب اختيار نوع السؤال')])
    points = IntegerField('الدرجة', validators=[
        DataRequired(message='يجب تحديد درجة السؤال'),
        NumberRange(min=1, max=10, message='يجب أن تكون الدرجة بين 1 و 10')
    ], default=1)
    question_image = FileField('صورة السؤال (اختياري)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'يجب أن تكون الصورة من نوع jpg، jpeg، png، أو gif فقط.')
    ])
    submit = SubmitField('إضافة السؤال')

class QuestionChoiceForm(FlaskForm):
    """Form for adding choices to a multiple choice question"""
    choice_text = TextAreaField('الخيار', validators=[
        DataRequired(message='يجب إدخال نص الخيار'),
        Length(min=1, max=200, message='يجب أن يكون الخيار بين 1 و 200 حرف')
    ])
    is_correct = BooleanField('الإجابة الصحيحة')
    submit = SubmitField('إضافة الخيار')

class TestAttemptForm(FlaskForm):
    """Form for submitting answers to a test"""
    submit = SubmitField('إنهاء الاختبار')

class TestAnswerForm(FlaskForm):
    """Form for handling individual test answers"""
    submit = SubmitField('حفظ الإجابات')

class TestTakingForm(FlaskForm):
    """Form for taking a test (includes hidden fields for test_id)"""
    test_id = HiddenField('معرف الاختبار', validators=[DataRequired()])
    submit = SubmitField('بدء الاختبار')

class TestRetryRequestForm(FlaskForm):
    """نموذج لطلب محاولة إضافية للاختبار"""
    test_id = HiddenField('معرف الاختبار', validators=[DataRequired()])
    reason = TextAreaField('سبب طلب المحاولة الإضافية', validators=[
        DataRequired(message='يرجى ذكر سبب طلب المحاولة الإضافية'),
        Length(min=10, max=500, message='يجب أن يكون السبب بين 10 و 500 حرف')
    ])
    submit = SubmitField('إرسال الطلب')

class TestRetryResponseForm(FlaskForm):
    """نموذج للرد على طلب محاولة إضافية للاختبار"""
    request_id = HiddenField('معرف الطلب', validators=[DataRequired()])
    admin_response = TextAreaField('الرد على الطلب', validators=[
        DataRequired(message='يرجى كتابة الرد على الطلب'),
        Length(min=5, max=500, message='يجب أن يكون الرد بين 5 و 500 حرف')
    ])
    status = SelectField('القرار', choices=[
        ('approved', 'الموافقة على الطلب'),
        ('rejected', 'رفض الطلب')
    ], validators=[DataRequired(message='يرجى اختيار القرار')])
    submit = SubmitField('إرسال الرد')