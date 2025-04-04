from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, URL, Optional, EqualTo, ValidationError, NumberRange
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

class AddPointsForm(FlaskForm):
    points = IntegerField('عدد النقاط', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('إضافة النقاط')

class VideoEditForm(FlaskForm):
    title = StringField('عنوان الفيديو', validators=[DataRequired(), Length(min=3, max=100)])
    url = StringField('رابط الفيديو', validators=[Optional(), URL()])
    description = TextAreaField('الوصف', validators=[Optional(), Length(max=2000)])
    requires_code = BooleanField('يتطلب كود للمشاهدة')
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
        Length(max=100, message='يجب أن لا يتجاوز البريد الإلكتروني 100 حرف')
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
