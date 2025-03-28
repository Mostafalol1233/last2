import logging
import os
import secrets
import string
import openai
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from app import db
from models import User, Video, Comment, Post, VideoView, LectureCode, VideoLike, StudentNote, AIChatMessage, DirectMessage
from forms import (
    LoginForm, VideoUploadForm, VideoEditForm, PostForm, CommentForm, RegistrationForm,
    LectureCodeForm, GenerateCodeForm, StudentNoteForm, AIChatForm, ForgotPasswordForm,
    ResetPasswordForm, ProfileForm, DirectMessageForm
)

# إعداد OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Create blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)
student_bp = Blueprint('student', __name__)

# Helper functions
def save_video_file(file):
    """Save the uploaded video file and return the path"""
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(file.filename)
    filename = random_hex + file_ext
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    file_path = os.path.join(uploads_dir, filename)
    file.save(file_path)
    
    # Return the relative path for storing in the database
    return os.path.join('uploads', filename)

def generate_random_code(length=8):
    """Generate a random code for lecture access"""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))
    
def handle_simple_queries(message):
    """معالجة الاستعلامات البسيطة دون الحاجة إلى OpenAI API"""
    import re
    import math
    
    # تبسيط النص وإزالة الزوائد
    message = message.strip().lower()
    
    # التحيات والمقدمات
    greetings = ['السلام', 'مرحبا', 'اهلا', 'اهلين', 'صباح الخير', 'مساء الخير', 'هاي', 'هلو']
    for greeting in greetings:
        if greeting in message:
            return f"{greeting} وسهلاً بك! أنا المساعد الذكي لمنصة الأستاذ أحمد حلي التعليمية. كيف يمكنني مساعدتك اليوم؟"
    
    # أسئلة عن هوية المساعد
    identity_questions = ['من انت', 'من أنت', 'عرف نفسك', 'عرف بنفسك', 'من انتم', 'من أنتم']
    for question in identity_questions:
        if question in message:
            return "أنا المساعد الذكي لمنصة الأستاذ أحمد حلي التعليمية. أساعد الطلاب في فهم المواد ودروس الأستاذ أحمد حلي والإجابة على أسئلتهم."
    
    # العمليات الحسابية البسيطة
    # للجمع: مثال "كم يساوي 2+3" أو "2 + 3"
    addition_match = re.search(r'(\d+)\s*\+\s*(\d+)', message)
    if addition_match:
        try:
            num1 = int(addition_match.group(1))
            num2 = int(addition_match.group(2))
            result = num1 + num2
            return f"ناتج جمع {num1} و {num2} هو {result}"
        except:
            pass
    
    # للطرح: مثال "كم يساوي 5-2" أو "5 - 2"
    subtraction_match = re.search(r'(\d+)\s*\-\s*(\d+)', message)
    if subtraction_match:
        try:
            num1 = int(subtraction_match.group(1))
            num2 = int(subtraction_match.group(2))
            result = num1 - num2
            return f"ناتج طرح {num2} من {num1} هو {result}"
        except:
            pass
    
    # للضرب: مثال "كم يساوي 3*4" أو "3 × 4"
    multiplication_match = re.search(r'(\d+)\s*[\*×]\s*(\d+)', message)
    if multiplication_match:
        try:
            num1 = int(multiplication_match.group(1))
            num2 = int(multiplication_match.group(2))
            result = num1 * num2
            return f"ناتج ضرب {num1} في {num2} هو {result}"
        except:
            pass
    
    # للقسمة: مثال "كم يساوي 8/2" أو "8 ÷ 2"
    division_match = re.search(r'(\d+)\s*[\/÷]\s*(\d+)', message)
    if division_match:
        try:
            num1 = int(division_match.group(1))
            num2 = int(division_match.group(2))
            if num2 == 0:
                return "لا يمكن القسمة على صفر"
            result = num1 / num2
            # إذا كانت النتيجة عدد صحيح، نعرضها كعدد صحيح
            if result.is_integer():
                return f"ناتج قسمة {num1} على {num2} هو {int(result)}"
            else:
                return f"ناتج قسمة {num1} على {num2} هو {result:.2f}"
        except:
            pass
    
    # القوانين الرياضية (بالإنجليزية)
    # نظرية فيثاغورس
    pythagorean_keywords = ['فيثاغورس', 'نظرية فيثاغورس', 'pythagoras', 'pythagorean']
    if any(keyword in message for keyword in pythagorean_keywords):
        return """**Pythagorean Theorem**
        
The Pythagorean theorem states that in a right-angled triangle, the square of the length of the hypotenuse equals the sum of squares of the lengths of the other two sides.

Formula: c² = a² + b²

Where:
- c is the length of the hypotenuse
- a and b are the lengths of the other two sides

Example:
If a = 3 and b = 4, then c² = 3² + 4² = 9 + 16 = 25
Therefore, c = 5"""

    # مساحة المثلث
    triangle_area_keywords = ['مساحة المثلث', 'triangle area', 'قانون مساحة المثلث']
    if any(keyword in message for keyword in triangle_area_keywords):
        return """**Triangle Area Formulas**

1. Base and Height Method:
   Area = (1/2) × base × height
   
2. Using Three Sides (Heron's Formula):
   Area = √(s(s-a)(s-b)(s-c))
   Where s = (a + b + c)/2 and a, b, c are the sides

3. Using Two Sides and the Included Angle:
   Area = (1/2) × a × b × sin(C)
   Where C is the included angle"""

    # مساحة ومحيط الدائرة
    circle_keywords = ['مساحة الدائرة', 'محيط الدائرة', 'circle area', 'circle circumference']
    if any(keyword in message for keyword in circle_keywords):
        return """**Circle Formulas**

Area = π × r²
Circumference = 2π × r

Where:
- r is the radius of the circle
- π (pi) is approximately 3.14159

Example:
For a circle with radius 5 units:
- Area = π × 5² = 25π ≈ 78.54 square units
- Circumference = 2π × 5 = 10π ≈ 31.42 units"""

    # المعادلة التربيعية
    quadratic_keywords = ['المعادلة التربيعية', 'quadratic equation', 'حل المعادلة التربيعية']
    if any(keyword in message for keyword in quadratic_keywords):
        return """**Quadratic Equation Formula**

For a quadratic equation in the form: ax² + bx + c = 0

The solutions (roots) are given by:
x = (-b ± √(b² - 4ac)) / 2a

Where:
- a, b, and c are coefficients
- The discriminant b² - 4ac determines the nature of the roots:
  * If b² - 4ac > 0: Two real and distinct roots
  * If b² - 4ac = 0: One real root (repeated)
  * If b² - 4ac < 0: Two complex conjugate roots"""

    # المسافة بين نقطتين
    distance_keywords = ['المسافة بين نقطتين', 'distance formula', 'distance between points']
    if any(keyword in message for keyword in distance_keywords):
        return """**Distance Formula**

The distance between two points (x₁, y₁) and (x₂, y₂) is:

d = √[(x₂ - x₁)² + (y₂ - y₁)²]

Example:
For points (2, 3) and (5, 7):
d = √[(5 - 2)² + (7 - 3)²]
d = √[9 + 16]
d = √25 = 5 units"""

    # قوانين حساب المثلثات
    trigonometry_keywords = ['حساب المثلثات', 'trigonometry', 'نسب مثلثية', 'trig', 'قوانين المثلثات']
    if any(keyword in message for keyword in trigonometry_keywords):
        return """**Basic Trigonometric Formulas**

In a right triangle:
- sin(θ) = opposite/hypotenuse
- cos(θ) = adjacent/hypotenuse
- tan(θ) = opposite/adjacent

Pythagorean Identities:
- sin²(θ) + cos²(θ) = 1
- 1 + tan²(θ) = sec²(θ)
- 1 + cot²(θ) = csc²(θ)

Law of Sines:
sin(A)/a = sin(B)/b = sin(C)/c

Law of Cosines:
c² = a² + b² - 2ab·cos(C)"""

    # الاشتقاق
    derivative_keywords = ['اشتقاق', 'derivative', 'calculus', 'تفاضل']
    if any(keyword in message for keyword in derivative_keywords):
        return """**Basic Derivatives**

1. d/dx(xⁿ) = n·xⁿ⁻¹
2. d/dx(sin x) = cos x
3. d/dx(cos x) = -sin x
4. d/dx(eˣ) = eˣ
5. d/dx(ln x) = 1/x

Chain Rule:
If y = f(g(x)), then dy/dx = (df/dg)·(dg/dx)

Product Rule:
If y = f(x)·g(x), then dy/dx = f(x)·g'(x) + g(x)·f'(x)

Quotient Rule:
If y = f(x)/g(x), then dy/dx = [g(x)·f'(x) - f(x)·g'(x)]/[g(x)]²"""

    # التكامل
    integral_keywords = ['تكامل', 'integral', 'integration']
    if any(keyword in message for keyword in integral_keywords):
        return """**Basic Integrals**

1. ∫ xⁿ dx = (x^(n+1))/(n+1) + C, where n ≠ -1
2. ∫ 1/x dx = ln|x| + C
3. ∫ eˣ dx = eˣ + C
4. ∫ sin x dx = -cos x + C
5. ∫ cos x dx = sin x + C

Substitution Method:
∫ f(g(x))·g'(x) dx = ∫ f(u) du, where u = g(x)

Integration by Parts:
∫ u dv = uv - ∫ v du"""

    # المتواليات والمتسلسلات
    sequence_keywords = ['متوالية', 'متسلسلة', 'sequence', 'series']
    if any(keyword in message for keyword in sequence_keywords):
        return """**Sequence and Series Formulas**

Arithmetic Sequence:
- nth term: aₙ = a₁ + (n - 1)d
- Sum of n terms: Sₙ = (n/2)·(a₁ + aₙ) = (n/2)·[2a₁ + (n - 1)d]

Geometric Sequence:
- nth term: aₙ = a₁·rⁿ⁻¹
- Sum of n terms: Sₙ = a₁·(1 - rⁿ)/(1 - r), for r ≠ 1
- Sum of infinite terms: S∞ = a₁/(1 - r), for |r| < 1

Binomial Theorem:
(a + b)ⁿ = ∑(k=0 to n) (n choose k)·aⁿ⁻ᵏ·bᵏ"""

    # الحجوم والمساحات السطحية
    volume_keywords = ['حجم', 'مساحة سطحية', 'volume', 'surface area']
    if any(keyword in message for keyword in volume_keywords):
        return """**Volume and Surface Area Formulas**

Cube:
- Volume = s³
- Surface Area = 6s²
Where s is the side length

Rectangular Prism:
- Volume = l × w × h
- Surface Area = 2(lw + lh + wh)
Where l, w, h are length, width, and height

Sphere:
- Volume = (4/3)πr³
- Surface Area = 4πr²
Where r is the radius

Cylinder:
- Volume = πr²h
- Surface Area = 2πr² + 2πrh
Where r is the radius and h is the height

Cone:
- Volume = (1/3)πr²h
- Surface Area = πr² + πrl
Where l is the slant height and l = √(r² + h²)"""

    # قوانين الحركة
    physics_motion_keywords = ['قوانين الحركة', 'motion', 'قوانين نيوتن', 'newton']
    if any(keyword in message for keyword in physics_motion_keywords):
        return """**Laws of Motion and Kinematics**

Newton's Laws:
1. An object at rest stays at rest, and an object in motion stays in motion with the same speed and direction unless acted upon by an unbalanced force.
2. F = ma (Force equals mass times acceleration)
3. For every action, there is an equal and opposite reaction.

Kinematics Equations (constant acceleration):
1. v = v₀ + at
2. d = v₀t + (1/2)at²
3. v² = v₀² + 2ad
4. d = (v₀ + v)t/2

Where:
- v is final velocity
- v₀ is initial velocity
- a is acceleration
- t is time
- d is displacement"""

    # لم يتم التعرف على السؤال كسؤال بسيط
    return None

# Main routes
@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
            
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        
        login_user(user)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.role == 'admin':
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('student.dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
            
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if username already exists
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('اسم المستخدم موجود بالفعل. برجاء اختيار اسم آخر.', 'danger')
                return render_template('register.html', form=form)
                
            user = User(
                username=form.username.data,
                role='student',
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            # Store credentials in session for auto-fill
            flash('تم تسجيل الحساب بنجاح! يمكنك الآن تسجيل الدخول باستخدام بياناتك.', 'success')
            return redirect(url_for('main.login', 
                username=form.username.data,
                password=form.password.data))
                
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء التسجيل. برجاء التأكد من البيانات وإعادة المحاولة.', 'danger')
            print(f"Registration error: {str(e)}")
    
    return render_template('register.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('main.login'))

# Admin routes
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        abort(403)
    
    videos = Video.query.order_by(Video.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    # جمع إحصائيات المشاهدات لكل فيديو
    video_stats = {}
    for video in videos:
        views = VideoView.query.filter_by(video_id=video.id).all()
        viewers = User.query.join(VideoView, User.id == VideoView.user_id).filter(VideoView.video_id == video.id).all()
        
        # الحصول على أكواد الوصول النشطة لكل فيديو
        active_codes = LectureCode.query.filter_by(video_id=video.id, is_active=True).all()
        
        video_stats[video.id] = {
            'views_count': len(views),
            'viewers': viewers,
            'active_codes': active_codes
        }
    
    return render_template('admin/dashboard.html', videos=videos, posts=posts, video_stats=video_stats)

@admin_bp.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    if not current_user.is_admin():
        abort(403)
        
    form = VideoUploadForm()
    if form.validate_on_submit():
        video = Video(
            title=form.title.data,
            description=form.description.data,
            uploaded_by=current_user.id,
            requires_code=form.requires_code.data
        )
        
        # معالجة رفع الفيديو كملف أو إضافة رابط
        if form.video_file.data:
            file_path = save_video_file(form.video_file.data)
            video.file_path = file_path
        else:
            video.url = form.url.data
            
        db.session.add(video)
        db.session.commit()
        
        # إذا كان الفيديو يتطلب كود للوصول، نقوم بإنشاء كود جديد
        if form.requires_code.data:
            code = generate_random_code()
            lecture_code = LectureCode(
                video_id=video.id,
                code=code,
                is_active=True
            )
            db.session.add(lecture_code)
            db.session.commit()
            flash(f'تم رفع الفيديو بنجاح! كود الوصول للمحاضرة هو: {code}', 'success')
        else:
            flash('تم رفع الفيديو بنجاح!', 'success')
            
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/upload_video.html', form=form)

@admin_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_admin():
        abort(403)
        
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            created_by=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_post.html', form=form)

@admin_bp.route('/delete_video/<int:video_id>')
@login_required
def delete_video(video_id):
    if not current_user.is_admin():
        abort(403)
        
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    if not current_user.is_admin():
        abort(403)
        
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('تم حذف المنشور بنجاح!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/generate_lecture_code/<int:video_id>', methods=['GET', 'POST'])
@login_required
def create_lecture_code(video_id):
    if not current_user.is_admin():
        abort(403)
        
    video = Video.query.get_or_404(video_id)
    
    form = GenerateCodeForm()
    # إحضار قائمة بالطلاب لعرضها في القائمة المنسدلة
    students = User.query.filter_by(role='student').all()
    form.student_id.choices = [(0, 'بدون تعيين لطالب محدد')] + [(s.id, s.full_name + ' (' + s.username + ')') for s in students]
    form.selected_students.choices = [(s.id, s.full_name + ' (' + s.username + ')') for s in students]
    
    if form.validate_on_submit():
        generated_codes = []
        student_id = form.student_id.data
        multiple_students = form.multiple_students.data
        num_codes = form.num_codes.data
        generate_pdf = form.generate_pdf.data
        selected_students = form.selected_students.data

        # إذا كان التوليد لعدة أكواد
        if multiple_students:
            # التحقق مما إذا كان المستخدم قد حدد طلابًا محددين
            if selected_students:
                # إنشاء كود لكل طالب محدد
                for student_id in selected_students:
                    code = generate_random_code()
                    lecture_code = LectureCode(
                        video_id=video.id,
                        code=code,
                        is_active=True,
                        is_used=False,
                        assigned_to=student_id
                    )
                    db.session.add(lecture_code)
                    student = User.query.get(student_id)
                    generated_codes.append({
                        'code': code,
                        'student': student.full_name if student else None,
                        'student_username': student.username if student else None
                    })
                
                db.session.commit()
                
                # إنشاء ملف PDF إذا طلب المستخدم ذلك
                if generate_pdf:
                    pdf_path = generate_codes_pdf(generated_codes, video.title, with_students=True)
                    flash(f'تم إنشاء {len(selected_students)} كود وتعيينهم للطلاب المحددين بنجاح!', 'success')
                    return send_file(pdf_path, as_attachment=True, download_name=f'lecture_codes_{video.id}.pdf')
                else:
                    flash(f'تم إنشاء {len(selected_students)} كود وتعيينهم للطلاب المحددين بنجاح!', 'success')
                    return redirect(url_for('admin.lecture_codes'))
            else:
                # إنشاء أكواد بدون تعيين لطلاب محددين
                for _ in range(num_codes):
                    code = generate_random_code()
                    lecture_code = LectureCode(
                        video_id=video.id,
                        code=code,
                        is_active=True,
                        is_used=False
                    )
                    db.session.add(lecture_code)
                    generated_codes.append({'code': code})
                
                db.session.commit()
                
                # إنشاء ملف PDF إذا طلب المستخدم ذلك
                if generate_pdf:
                    pdf_path = generate_codes_pdf(generated_codes, video.title, with_students=False)
                    flash(f'تم إنشاء {num_codes} كود بنجاح!', 'success')
                    return send_file(pdf_path, as_attachment=True, download_name=f'lecture_codes_{video.id}.pdf')
                else:
                    flash(f'تم إنشاء {num_codes} كود بنجاح!', 'success')
                    return redirect(url_for('admin.lecture_codes'))
        else:
            # إنشاء كود واحد (السلوك القديم)
            code = generate_random_code()
            lecture_code = LectureCode(
                video_id=video.id,
                code=code,
                is_active=True,
                is_used=False
            )
            
            # في حالة إذا تم تحديد طالب معين
            if student_id != 0:
                lecture_code.assigned_to = student_id
                student = User.query.get(student_id)
                success_message = f'تم إنشاء كود جديد للمحاضرة وتعيينه للطالب {student.full_name}: {code}'
            else:
                success_message = f'تم إنشاء كود جديد للمحاضرة: {code}'
                
            db.session.add(lecture_code)
            db.session.commit()
            
            flash(success_message, 'success')
            return redirect(url_for('admin.lecture_codes'))
    
    # في حالة GET
    form.video_id.data = video_id
    return render_template('admin/generate_code.html', form=form, video=video)

def generate_codes_pdf(codes, video_title, with_students=False):
    """إنشاء ملف PDF يحتوي على أكواد المحاضرات، مع إمكانية عرض أسماء الطلاب المعينين للأكواد"""
    import os
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # تحديد مسار الملف في مجلد مؤقت
    pdf_path = 'static/temp/lecture_codes.pdf'
    
    # إعداد مستند PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # إنشاء العناصر التي ستظهر في PDF
    elements = []
    
    # إضافة عنوان
    title_style = styles['Heading1']
    title = Paragraph(f"أكواد المحاضرة: {video_title}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # إنشاء بيانات الجدول
    if with_students:
        data = [['رقم', 'كود المحاضرة', 'اسم الطالب']]
        for i, code_info in enumerate(codes, 1):
            student_name = code_info.get('student', '')
            data.append([str(i), code_info['code'], student_name])
        # تعديل عرض الجدول ليتناسب مع وجود عمود إضافي
        col_widths = [40, 150, 200]
    else:
        data = [['رقم', 'كود المحاضرة']]
        for i, code_info in enumerate(codes, 1):
            if isinstance(code_info, dict):
                data.append([str(i), code_info['code']])
            else:
                data.append([str(i), code_info])
        col_widths = [60, 200]
    
    # إنشاء جدول مع تنسيق
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    
    # إضافة معلومات إضافية
    elements.append(Spacer(1, 30))
    notes = Paragraph("ملاحظة: هذه الأكواد للاستخدام لمرة واحدة فقط، الرجاء الاحتفاظ بها بعناية.", styles["Normal"])
    elements.append(notes)
    
    # إضافة تاريخ إنشاء الأكواد
    elements.append(Spacer(1, 10))
    import datetime
    creation_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    date_note = Paragraph(f"تم إنشاء هذه الأكواد بتاريخ: {creation_date}", styles["Normal"])
    elements.append(date_note)
    
    # بناء المستند
    doc.build(elements)
    
    return pdf_path

@admin_bp.route('/deactivate_code/<int:code_id>')
@login_required
def deactivate_code(code_id):
    if not current_user.is_admin():
        abort(403)
        
    code = LectureCode.query.get_or_404(code_id)
    code.is_active = False
    db.session.commit()
    
    flash('تم إلغاء تنشيط الكود بنجاح.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_stats/<int:video_id>')
@login_required
def view_stats(video_id):
    if not current_user.is_admin():
        abort(403)
        
    video = Video.query.get_or_404(video_id)
    views = VideoView.query.filter_by(video_id=video_id).order_by(VideoView.viewed_at.desc()).all()
    viewers = User.query.join(VideoView, User.id == VideoView.user_id).filter(VideoView.video_id == video_id).all()
    
    return render_template('admin/video_stats.html', video=video, views=views, viewers=viewers)

@admin_bp.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    if not current_user.is_admin():
        abort(403)
        
    video = Video.query.get_or_404(video_id)
    form = VideoEditForm()
    
    if request.method == 'GET':
        form.title.data = video.title
        form.url.data = video.url
        form.description.data = video.description
        form.requires_code.data = video.requires_code
    
    if form.validate_on_submit():
        # تحديث بيانات الفيديو
        video.title = form.title.data
        video.url = form.url.data
        video.description = form.description.data
        
        # التحقق من تغيير خاصية "يتطلب كود"
        if not video.requires_code and form.requires_code.data:
            # تغيير من عام إلى خاص - إنشاء كود جديد
            video.requires_code = True
            code = generate_random_code()
            lecture_code = LectureCode(
                video_id=video.id,
                code=code,
                is_active=True
            )
            db.session.add(lecture_code)
            db.session.commit()
            flash(f'تم تحديث الفيديو وتعيينه كمحاضرة خاصة. كود الوصول الجديد: {code}', 'success')
        elif video.requires_code and not form.requires_code.data:
            # تغيير من خاص إلى عام - تعطيل الأكواد الحالية
            video.requires_code = False
            LectureCode.query.filter_by(video_id=video.id, is_active=True).update({'is_active': False})
            db.session.commit()
            flash('تم تحديث الفيديو وتعيينه كمحاضرة عامة (متاح للجميع بدون كود).', 'success')
        else:
            # تحديث عادي
            video.requires_code = form.requires_code.data
            db.session.commit()
            flash('تم تحديث بيانات الفيديو بنجاح!', 'success')
        
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_video.html', form=form, video=video)

# Student routes
@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
        
    videos = Video.query.order_by(Video.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    # تحديد الفيديوهات التي شاهدها الطالب بالفعل
    viewed_videos = set()
    user_views = VideoView.query.filter_by(user_id=current_user.id).all()
    for view in user_views:
        viewed_videos.add(view.video_id)
    
    return render_template('student/dashboard.html', videos=videos, posts=posts, viewed_videos=viewed_videos)
    
@student_bp.route('/dashboard/en')
@login_required
def dashboard_en():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
        
    videos = Video.query.order_by(Video.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    # Get list of videos that the student has already watched
    viewed_videos = set()
    user_views = VideoView.query.filter_by(user_id=current_user.id).all()
    for view in user_views:
        viewed_videos.add(view.video_id)
    
    return render_template('student/dashboard_en.html', videos=videos, posts=posts, viewed_videos=viewed_videos)

@student_bp.route('/video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def view_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    # التحقق مما إذا كان الفيديو يتطلب كود للوصول
    if video.requires_code:
        # البحث عن محاولة مشاهدة سابقة
        view = VideoView.query.filter_by(video_id=video_id, user_id=current_user.id).first()
        if not view:
            # لم يشاهد الفيديو من قبل، يجب إدخال الكود
            return redirect(url_for('student.enter_lecture_code', video_id=video_id))
    
    # يمكن مشاهدة الفيديو، تسجيل المشاهدة إذا لم تكن موجودة بالفعل
    view = VideoView.query.filter_by(video_id=video_id, user_id=current_user.id).first()
    if not view:
        view = VideoView(
            video_id=video_id,
            user_id=current_user.id
        )
        db.session.add(view)
        db.session.commit()
    
    # استمارة التعليق
    form = CommentForm()
    form.video_id.data = video_id
    
    if form.validate_on_submit():
        comment = Comment(
            video_id=video_id,
            user_id=current_user.id,
            comment_text=form.comment_text.data
        )
        db.session.add(comment)
        db.session.commit()
        flash('تم إضافة التعليق بنجاح!', 'success')
        return redirect(url_for('student.view_video', video_id=video_id))
    
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
    
    # جلب الفيديوهات الأخرى للعرض في الشريط الجانبي
    other_videos = Video.query.filter(Video.id != video_id).order_by(Video.created_at.desc()).limit(5).all()
    
    return render_template('student/video.html', video=video, form=form, comments=comments, other_videos=other_videos)

@student_bp.route('/enter_lecture_code/<int:video_id>', methods=['GET', 'POST'])
@login_required
def enter_lecture_code(video_id):
    video = Video.query.get_or_404(video_id)
    
    if not video.requires_code:
        return redirect(url_for('student.view_video', video_id=video_id))
    
    form = LectureCodeForm()
    form.video_id.data = video_id
    
    if form.validate_on_submit():
        # التحقق من الكود
        code = form.code.data
        lecture_code = None
        if code:
            code = code.strip().upper()
            # التحقق من كود عام أو كود مخصص للطالب
            lecture_code = LectureCode.query.filter_by(
                video_id=video_id, 
                code=code, 
                is_active=True
            ).first()
            
            if lecture_code:
                # التحقق إذا كان الكود مخصص لطالب محدد
                if lecture_code.assigned_to is not None and lecture_code.assigned_to != current_user.id:
                    flash('عذراً، هذا الكود مخصص لطالب آخر ولا يمكنك استخدامه.', 'danger')
                    return render_template('student/enter_lecture_code.html', video=video, form=form)
                
                # الكود صحيح، تسجيل المشاهدة
                view = VideoView(
                    video_id=video_id,
                    user_id=current_user.id
                )
                db.session.add(view)
                
                # جعل الكود غير فعال بعد الاستخدام (استخدام مرة واحدة)
                lecture_code.is_active = False
                lecture_code.is_used = True
                
                db.session.commit()
                flash('تم التحقق من الكود بنجاح! يمكنك مشاهدة المحاضرة الآن.', 'success')
                return redirect(url_for('student.view_video', video_id=video_id))
            else:
                # الكود غير صحيح
                flash('عذراً، الكود غير صحيح أو غير نشط. الرجاء التحقق والمحاولة مرة أخرى.', 'danger')
    
    return render_template('student/enter_lecture_code.html', video=video, form=form)

@student_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # جلب المنشورات الأخرى للعرض في الشريط الجانبي
    other_posts = Post.query.filter(Post.id != post_id).order_by(Post.created_at.desc()).limit(5).all()
    
    # جلب أحدث الفيديوهات للعرض في الشريط الجانبي
    recent_videos = Video.query.order_by(Video.created_at.desc()).limit(5).all()
    
    return render_template('student/post.html', post=post, other_posts=other_posts, recent_videos=recent_videos)
@admin_bp.route('/users_list')
@login_required
def users_list():
    if not current_user.is_admin():
        abort(403)
    users = User.query.all()
    print("\nقائمة المستخدمين:")
    print("================")
    for user in users:
        print(f"اسم المستخدم: {user.username}")
        print(f"الاسم الكامل: {user.full_name}")
        print(f"نوع المستخدم: {'مشرف' if user.role == 'admin' else 'طالب'}")
        print("----------------")
    return render_template('admin/users_list.html', users=users)

# صفحة أكواد المحاضرات للمشرف
@admin_bp.route('/lecture_codes')
@login_required
def lecture_codes():
    if not current_user.is_admin():
        abort(403)
    
    # جلب كل الفيديوهات والأكواد
    videos = Video.query.filter_by(requires_code=True).all()
    active_codes = LectureCode.query.filter_by(is_active=True).order_by(LectureCode.created_at.desc()).all()
    inactive_codes = LectureCode.query.filter_by(is_active=False).order_by(LectureCode.created_at.desc()).all()
    
    return render_template(
        'admin/lecture_codes.html', 
        videos=videos, 
        active_codes=active_codes, 
        inactive_codes=inactive_codes
    )

# إضافة ميزة اللايك للفيديوهات
@student_bp.route('/like_video/<int:video_id>', methods=['POST'])
@login_required
def like_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    # التحقق مما إذا كان المستخدم قد أعجب بالفيديو من قبل
    existing_like = VideoLike.query.filter_by(video_id=video_id, user_id=current_user.id).first()
    
    if existing_like:
        # إلغاء الإعجاب
        db.session.delete(existing_like)
        db.session.commit()
        flash('تم إلغاء الإعجاب بنجاح', 'info')
    else:
        # إضافة إعجاب جديد
        like = VideoLike(video_id=video_id, user_id=current_user.id)
        db.session.add(like)
        db.session.commit()
        flash('تم تسجيل إعجابك بنجاح', 'success')
    
    return redirect(url_for('student.view_video', video_id=video_id))

# ميزة الملاحظات الشخصية
@student_bp.route('/notes', methods=['GET'])
@login_required
def view_notes():
    notes = StudentNote.query.filter_by(user_id=current_user.id).order_by(StudentNote.updated_at.desc()).all()
    form = StudentNoteForm()
    return render_template('student/notes.html', notes=notes, form=form)
    
# صفحة القوانين الرياضية العامة (عربي)
@student_bp.route('/formulas')
@login_required
def math_formulas():
    return render_template('student/formulas.html')
    
# صفحة قوانين الجبر للمرحلة الثانوية (عربي)
@student_bp.route('/algebra_formulas')
@login_required
def algebra_formulas():
    return render_template('student/algebra_formulas.html')

# صفحة قوانين متقدمة (تفاضل وتكامل، ميكانيكا، ديناميكا) (عربي)
@student_bp.route('/advanced_formulas')
@login_required
def advanced_formulas():
    return render_template('student/advanced_formulas.html')
    
# صفحة القوانين الرياضية العامة (إنجليزي)
@student_bp.route('/formulas/en')
@login_required
def math_formulas_en():
    return render_template('student/formulas_en.html')
    
# صفحة قوانين الجبر للمرحلة الثانوية (إنجليزي)
@student_bp.route('/algebra_formulas/en')
@login_required
def algebra_formulas_en():
    return render_template('student/algebra_formulas_en.html')
    
# صفحة قوانين متقدمة (تفاضل وتكامل، ميكانيكا، ديناميكا) (إنجليزي)
@student_bp.route('/advanced_formulas/en')
@login_required
def advanced_formulas_en():
    return render_template('student/advanced_formulas_en.html')
    
# صفحة الآلة الحاسبة المتقدمة (عربي)
@student_bp.route('/calculator')
@login_required
def advanced_calculator():
    return render_template('student/advanced_calculator.html')
    
# صفحة الآلة الحاسبة المتقدمة (إنجليزي)
@student_bp.route('/calculator/en')
@login_required
def advanced_calculator_en():
    return render_template('student/advanced_calculator_en.html')

@student_bp.route('/notes/add', methods=['POST'])
@login_required
def add_note():
    form = StudentNoteForm()
    if form.validate_on_submit():
        note = StudentNote(
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(note)
        db.session.commit()
        flash('تم إضافة الملاحظة بنجاح', 'success')
    return redirect(url_for('student.view_notes'))

@student_bp.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = StudentNote.query.get_or_404(note_id)
    
    # التأكد من أن المستخدم هو صاحب الملاحظة
    if note.user_id != current_user.id:
        abort(403)
    
    form = StudentNoteForm()
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('تم تحديث الملاحظة بنجاح', 'success')
        return redirect(url_for('student.view_notes'))
    
    form.title.data = note.title
    form.content.data = note.content
    return render_template('student/edit_note.html', form=form, note=note)

@student_bp.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = StudentNote.query.get_or_404(note_id)
    
    # التأكد من أن المستخدم هو صاحب الملاحظة
    if note.user_id != current_user.id:
        abort(403)
    
    db.session.delete(note)
    db.session.commit()
    flash('تم حذف الملاحظة بنجاح', 'success')
    return redirect(url_for('student.view_notes'))

# ميزة الدردشة الذكية
@student_bp.route('/ai_chat', methods=['GET', 'POST'])
@login_required
def ai_chat():
    form = AIChatForm()
    
    if form.validate_on_submit():
        message = form.message.data
        
        # معالجة الأسئلة البسيطة بدون الحاجة إلى OpenAI API
        simple_response = handle_simple_queries(message)
        
        if simple_response:
            response = simple_response
        else:
            try:
                # استخدام OpenAI API للحصول على إجابة (الإصدار 0.28)
                chat_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "أنت مساعد تعليمي متخصص في مساعدة الطلاب. قدم إجابات موجزة ومفيدة باللغة العربية. أنت تمثل المساعد الذكي لمنصة الأستاذ أحمد حلي التعليمية."},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                response = chat_response.choices[0].message['content']
            except Exception as e:
                # في حالة حدوث خطأ مع API
                print(f"خطأ في OpenAI API: {str(e)}")
                response = "عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى لاحقاً."
        
        # حفظ المحادثة في قاعدة البيانات
        chat_message = AIChatMessage(
            user_id=current_user.id,
            message=message,
            response=response
        )
        db.session.add(chat_message)
        db.session.commit()
        
        flash('تم إرسال سؤالك بنجاح', 'success')
        
    # جلب آخر 10 رسائل للمستخدم
    messages = AIChatMessage.query.filter_by(user_id=current_user.id).order_by(AIChatMessage.created_at.desc()).limit(10).all()
    messages.reverse()  # عرض الرسائل بترتيب تصاعدي
    
    return render_template('student/ai_chat.html', form=form, messages=messages)

# مسارات استعادة كلمة المرور
@main_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            # التحقق من تطابق البريد الإلكتروني ورقم الهاتف مع المعلومات المسجلة بالفعل
            if (user.email and user.email == form.email.data) or (user.phone and user.phone == form.phone.data):
                # توليد رمز استعادة وحفظه
                token = user.generate_reset_token()
                db.session.commit()
                
                # إعادة توجيه المستخدم مباشرة إلى صفحة إعادة تعيين كلمة المرور
                return redirect(url_for('main.reset_password', token=token, username=user.username))
            else:
                flash('المعلومات المدخلة غير متطابقة مع معلومات الحساب. يرجى التأكد من صحة البريد الإلكتروني ورقم الهاتف.', 'danger')
        else:
            flash('لم يتم العثور على حساب بهذا الاسم.', 'danger')
            
    return render_template('forgot_password.html', form=form)

@main_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    username = request.args.get('username')
    if not username:
        flash('رابط استعادة غير صالح.', 'danger')
        return redirect(url_for('main.login'))
        
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_reset_token(token):
        flash('رابط استعادة غير صالح أو منتهي الصلاحية.', 'danger')
        return redirect(url_for('main.login'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول باستخدام كلمة المرور الجديدة.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('reset_password.html', form=form)

# مسارات الملف الشخصي
@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        db.session.commit()
        flash('تم تحديث بياناتك الشخصية بنجاح.', 'success')
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html', form=form)

# نظام الرسائل المباشرة
@main_bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    # إنشاء نموذج إرسال رسالة جديدة
    form = DirectMessageForm()
    
    # تعبئة قائمة المستخدمين للاختيار منها (المشرفين للطلاب، والطلاب للمشرفين)
    if current_user.is_admin():
        # المشرف يمكنه الإرسال للطلاب فقط
        recipients = User.query.filter_by(role='student').all()
    else:
        # الطالب يمكنه الإرسال للمشرفين فقط
        recipients = User.query.filter_by(role='admin').all()
    
    form.recipient_id.choices = [(user.id, user.full_name + ' (' + user.username + ')') for user in recipients]
    
    if form.validate_on_submit():
        message = DirectMessage(
            sender_id=current_user.id,
            recipient_id=form.recipient_id.data,
            message=form.message.data,
            is_read=False
        )
        db.session.add(message)
        db.session.commit()
        flash('تم إرسال الرسالة بنجاح', 'success')
        return redirect(url_for('main.messages'))
    
    # جلب الرسائل المستلمة والمرسلة
    received_messages = DirectMessage.query.filter_by(recipient_id=current_user.id).order_by(DirectMessage.created_at.desc()).all()
    sent_messages = DirectMessage.query.filter_by(sender_id=current_user.id).order_by(DirectMessage.created_at.desc()).all()
    
    # تعليم الرسائل المستلمة كمقروءة
    for msg in received_messages:
        if not msg.is_read:
            msg.is_read = True
    
    db.session.commit()
    
    return render_template('messages.html', 
                          form=form, 
                          received_messages=received_messages, 
                          sent_messages=sent_messages)

@main_bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = DirectMessage.query.get_or_404(message_id)
    
    # التأكد من أن المستخدم هو المرسل أو المستلم للرسالة
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        abort(403)
    
    db.session.delete(message)
    db.session.commit()
    flash('تم حذف الرسالة بنجاح', 'success')
    
    return redirect(url_for('main.messages'))
