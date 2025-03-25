from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, URL, Optional, EqualTo, ValidationError
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
    submit = SubmitField('رفع الفيديو')

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
    submit = SubmitField('توليد كود جديد')
    
class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=3, max=64)])
    full_name = StringField('الاسم الثلاثي', validators=[DataRequired(), Length(min=5, max=100)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('نوع الحساب', choices=[('student', 'طالب')], validators=[DataRequired()])
    submit = SubmitField('تسجيل')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('هذا الاسم مستخدم بالفعل، يرجى اختيار اسم آخر')
