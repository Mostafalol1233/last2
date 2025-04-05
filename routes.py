import logging
import os
import secrets
import string
import openai
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from app import db, app
from models import (
    User, Video, Comment, Post, VideoView, LectureCode, VideoLike, StudentNote, 
    AIChatMessage, DirectMessage, PointTransfer, Test, TestQuestion, QuestionChoice,
    TestAttempt, TestAnswer
)
from forms import (
    LoginForm, VideoUploadForm, VideoEditForm, PostForm, CommentForm, RegistrationForm,
    LectureCodeForm, GenerateCodeForm, StudentNoteForm, AIChatForm, ForgotPasswordForm,
    ResetPasswordForm, ProfileForm, DirectMessageForm, TransferPointsForm, TestCreateForm,
    TestQuestionForm, QuestionChoiceForm, TestAttemptForm, TestTakingForm
)

# إعداد OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Create blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)
student_bp = Blueprint('student', __name__)

# Context processor to provide current date and time to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

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
    import requests
    import json
    
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
    
    # استخدام DuckDuckGo للاستعلامات البحثية
    search_indicators = ['ابحث عن', 'ما هو', 'من هو', 'اعرف لي', 'عرفني', 'معلومات عن']
    is_search = False
    search_query = message
    
    for indicator in search_indicators:
        if message.startswith(indicator):
            is_search = True
            search_query = message[len(indicator):].strip()
            break
    
    # إذا كان طلب بحث، استخدام DuckDuckGo API
    if is_search or len(message.split()) <= 5:  # استعلامات قصيرة محتمل أن تكون بحث
        try:
            url = f"https://api.duckduckgo.com/?q={search_query}&format=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                # تجميع النتائج
                results = []
                
                # الملخص الأساسي
                if data.get('Abstract'):
                    results.append(data['Abstract'])
                
                # معلومات إضافية
                if data.get('Definition'):
                    results.append(f"تعريف: {data['Definition']}")
                
                # روابط ذات صلة
                related_topics = data.get('RelatedTopics', [])
                if related_topics and len(related_topics) > 0:
                    topic_texts = [topic.get('Text') for topic in related_topics[:3] if topic.get('Text')]
                    if topic_texts:
                        results.append("مواضيع ذات صلة: " + " | ".join(topic_texts))
                
                # إذا وجدنا معلومات
                if results:
                    return "\n\n".join(results)
        except Exception as e:
            print(f"خطأ في استعلام DuckDuckGo: {str(e)}")
            # في حالة الخطأ، نستمر في الدالة للاستعلامات البسيطة الأخرى
    
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
            video.points_cost = form.points_cost.data
            db.session.commit()
            flash('تم تحديث بيانات الفيديو بنجاح!', 'success')
        
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_video.html', form=form, video=video)

# Admin Test Management Routes
@admin_bp.route('/tests')
@login_required
def manage_tests():
    if not current_user.is_admin():
        abort(403)
        
    tests = Test.query.order_by(Test.created_at.desc()).all()
    return render_template('admin/tests.html', tests=tests)

@admin_bp.route('/tests/create', methods=['GET', 'POST'])
@login_required
def create_test():
    if not current_user.is_admin():
        abort(403)
        
    form = TestCreateForm()
    if form.validate_on_submit():
        test = Test(
            title=form.title.data,
            description=form.description.data,
            created_by=current_user.id,
            time_limit_minutes=form.time_limit_minutes.data,
            passing_score=form.passing_score.data
        )
        db.session.add(test)
        db.session.commit()
        flash('تم إنشاء الاختبار بنجاح. يرجى إضافة أسئلة الآن.', 'success')
        return redirect(url_for('admin.edit_test', test_id=test.id))
        
    return render_template('admin/create_test.html', form=form)

@admin_bp.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    if not current_user.is_admin():
        abort(403)
        
    test = Test.query.get_or_404(test_id)
    form = TestCreateForm(obj=test)
    
    # Form for adding questions
    question_form = TestQuestionForm()
    
    if form.validate_on_submit():
        test.title = form.title.data
        test.description = form.description.data
        test.time_limit_minutes = form.time_limit_minutes.data
        test.passing_score = form.passing_score.data
        db.session.commit()
        flash('تم تحديث الاختبار بنجاح.', 'success')
        return redirect(url_for('admin.edit_test', test_id=test.id))
        
    return render_template('admin/edit_test.html', test=test, form=form, question_form=question_form)

@admin_bp.route('/tests/<int:test_id>/add_question', methods=['POST'])
@login_required
def add_question(test_id):
    if not current_user.is_admin():
        abort(403)
        
    test = Test.query.get_or_404(test_id)
    form = TestQuestionForm()
    
    if form.validate_on_submit():
        # Count questions to determine order
        next_order = TestQuestion.query.filter_by(test_id=test_id).count() + 1
        
        question = TestQuestion(
            test_id=test_id,
            question_text=form.question_text.data,
            question_type=form.question_type.data,
            points=form.points.data,
            order=next_order
        )
        db.session.add(question)
        db.session.commit()
        
        # If true/false question, automatically add Yes/No choices
        if form.question_type.data == 'true_false':
            true_choice = QuestionChoice(
                question_id=question.id,
                choice_text='صح',
                is_correct=True,
                order=1
            )
            false_choice = QuestionChoice(
                question_id=question.id,
                choice_text='خطأ',
                is_correct=False,
                order=2
            )
            db.session.add_all([true_choice, false_choice])
            db.session.commit()
            flash('تم إضافة سؤال صح/خطأ بنجاح.', 'success')
            return redirect(url_for('admin.edit_test', test_id=test_id))
        else:
            flash('تم إضافة السؤال بنجاح. يرجى إضافة الخيارات الآن.', 'success')
            return redirect(url_for('admin.edit_question', question_id=question.id))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"خطأ في حقل {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('admin.edit_test', test_id=test_id))

@admin_bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin():
        abort(403)
        
    question = TestQuestion.query.get_or_404(question_id)
    test = Test.query.get_or_404(question.test_id)
    
    form = TestQuestionForm(obj=question)
    choice_form = QuestionChoiceForm()
    
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.question_type = form.question_type.data
        question.points = form.points.data
        db.session.commit()
        flash('تم تحديث السؤال بنجاح.', 'success')
        
    return render_template('admin/edit_question.html', 
                          question=question, 
                          test=test, 
                          form=form, 
                          choice_form=choice_form)

@admin_bp.route('/questions/<int:question_id>/add_choice', methods=['POST'])
@login_required
def add_choice(question_id):
    if not current_user.is_admin():
        abort(403)
        
    question = TestQuestion.query.get_or_404(question_id)
    form = QuestionChoiceForm()
    
    if form.validate_on_submit():
        # Count choices to determine order
        next_order = QuestionChoice.query.filter_by(question_id=question_id).count() + 1
        
        choice = QuestionChoice(
            question_id=question_id,
            choice_text=form.choice_text.data,
            is_correct=form.is_correct.data,
            order=next_order
        )
        db.session.add(choice)
        db.session.commit()
        flash('تم إضافة الخيار بنجاح.', 'success')
    
    return redirect(url_for('admin.edit_question', question_id=question_id))

@admin_bp.route('/choices/<int:choice_id>/toggle_correct', methods=['POST'])
@login_required
def toggle_choice_correct(choice_id):
    if not current_user.is_admin():
        abort(403)
        
    choice = QuestionChoice.query.get_or_404(choice_id)
    
    # Toggle the current state
    choice.is_correct = not choice.is_correct
    
    # If this is a true/false question, ensure only one correct answer
    question = TestQuestion.query.get(choice.question_id)
    if question.question_type == 'true_false' and choice.is_correct:
        # Set all other choices to False
        for other_choice in question.choices.all():
            if other_choice.id != choice.id:
                other_choice.is_correct = False
    
    db.session.commit()
    return jsonify(success=True, is_correct=choice.is_correct)

@admin_bp.route('/choices/<int:choice_id>/delete', methods=['POST'])
@login_required
def delete_choice(choice_id):
    if not current_user.is_admin():
        abort(403)
        
    choice = QuestionChoice.query.get_or_404(choice_id)
    question_id = choice.question_id
    
    db.session.delete(choice)
    db.session.commit()
    flash('تم حذف الخيار بنجاح.', 'success')
    
    return redirect(url_for('admin.edit_question', question_id=question_id))

@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin():
        abort(403)
        
    question = TestQuestion.query.get_or_404(question_id)
    test_id = question.test_id
    
    # Delete all choices first due to foreign key constraints
    for choice in question.choices.all():
        db.session.delete(choice)
    
    db.session.delete(question)
    db.session.commit()
    flash('تم حذف السؤال بنجاح.', 'success')
    
    return redirect(url_for('admin.edit_test', test_id=test_id))

@admin_bp.route('/tests/<int:test_id>/delete', methods=['POST'])
@login_required
def delete_test(test_id):
    if not current_user.is_admin():
        abort(403)
        
    test = Test.query.get_or_404(test_id)
    
    # Delete all associated data (cascading delete)
    # - First delete answers
    for attempt in test.attempts.all():
        for answer in attempt.answers.all():
            db.session.delete(answer)
    
    # - Then delete attempts
    for attempt in test.attempts.all():
        db.session.delete(attempt)
    
    # - Then delete choices and questions
    for question in test.questions.all():
        for choice in question.choices.all():
            db.session.delete(choice)
        db.session.delete(question)
    
    # Finally delete the test
    db.session.delete(test)
    db.session.commit()
    flash('تم حذف الاختبار بنجاح.', 'success')
    
    return redirect(url_for('admin.manage_tests'))

@admin_bp.route('/tests/<int:test_id>/results')
@login_required
def test_results(test_id):
    if not current_user.is_admin():
        abort(403)
        
    test = Test.query.get_or_404(test_id)
    attempts = TestAttempt.query.filter_by(test_id=test_id).order_by(TestAttempt.completed_at.desc()).all()
    
    # Separate attempts into completed and in-progress
    completed_attempts = [a for a in attempts if a.completed_at is not None]
    in_progress_attempts = [a for a in attempts if a.completed_at is None]
    
    return render_template('admin/test_results.html', 
                           test=test, 
                           completed_attempts=completed_attempts,
                           in_progress_attempts=in_progress_attempts)

@admin_bp.route('/attempts/<int:attempt_id>/view')
@login_required
def view_attempt(attempt_id):
    attempt = TestAttempt.query.get_or_404(attempt_id)
    
    # Admins can view any attempt, students can only view their own
    if not current_user.is_admin() and attempt.user_id != current_user.id:
        abort(403)
    
    test = Test.query.get_or_404(attempt.test_id)
    answers = attempt.answers.all()
    
    return render_template('view_attempt.html', 
                          attempt=attempt, 
                          test=test, 
                          answers=answers)

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
    
    # التحقق مما إذا كان الفيديو يتطلب كود للوصول (للطلاب فقط)
    if video.requires_code and not current_user.is_admin():
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

@admin_bp.route('/add_points/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_points(user_id):
    if not current_user.is_admin():
        abort(403)
        
    student = User.query.get_or_404(user_id)
    if student.role != 'student':
        abort(404)
        
    form = AddPointsForm()
    if form.validate_on_submit():
        student.points += form.points.data
        db.session.commit()
        flash(f'تم إضافة {form.points.data} نقطة لحساب الطالب {student.full_name}', 'success')
        return redirect(url_for('admin.users_list'))
        
    return render_template('admin/add_points.html', form=form, student=student)

@student_bp.route('/buy_video/<int:video_id>')
@login_required
def buy_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    if not video.requires_code:
        return redirect(url_for('student.view_video', video_id=video_id))
        
    # التحقق من عدم شراء الفيديو مسبقاً
    existing_view = VideoView.query.filter_by(video_id=video_id, user_id=current_user.id).first()
    if existing_view:
        return redirect(url_for('student.view_video', video_id=video_id))
    
    # التحقق من امتلاك نقاط كافية
    if current_user.points < video.points_cost:
        flash('عذراً، لا تملك نقاط كافية لشراء هذا الفيديو', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # خصم النقاط وتسجيل المشاهدة
    current_user.points -= video.points_cost
    view = VideoView(video_id=video_id, user_id=current_user.id)
    db.session.add(view)
    db.session.commit()
    
    flash('تم شراء الفيديو بنجاح!', 'success')
    return redirect(url_for('student.view_video', video_id=video_id))

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
@admin_bp.route('/transfer_points', methods=['GET', 'POST'])
@login_required
def transfer_points():
    if not current_user.is_admin():
        abort(403)
        
    form = TransferPointsForm()
    form.student_id.choices = [(user.id, f"{user.full_name} ({user.username})") 
                              for user in User.query.filter_by(role='student').all()]
    
    if form.validate_on_submit():
        student = User.query.get(form.student_id.data)
        if student:
            # إضافة النقاط للطالب
            student.points += form.points.data
            
            # تسجيل عملية التحويل
            transfer = PointTransfer(
                student_id=student.id,
                points=form.points.data
            )
            db.session.add(transfer)
            db.session.commit()
            
            flash(f'تم تحويل {form.points.data} نقطة إلى الطالب {student.full_name} بنجاح', 'success')
            return redirect(url_for('admin.transfer_points'))
            
    transfers = PointTransfer.query.order_by(PointTransfer.created_at.desc()).all()
    return render_template('admin/transfer_points.html', form=form, transfers=transfers)

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
            # تحقق من وجود مفتاح OpenAI API
            if not openai.api_key:
                response = "لم يتم إعداد مفتاح OpenAI API بعد. يرجى الاتصال بمسؤول النظام."
                print("مفتاح OpenAI API غير معد")
            else:
                try:
                    # استخدام OpenAI API للحصول على إجابة (الإصدار الجديد)
                    from openai import OpenAI
                    client = OpenAI(api_key=openai.api_key)
                    
                    try:
                        # محاولة استخدام الواجهة الجديدة
                        chat_response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "أنت مساعد تعليمي متخصص في مساعدة الطلاب. قدم إجابات موجزة ومفيدة باللغة العربية. أنت تمثل المساعد الذكي لمنصة الأستاذ أحمد حلي التعليمية."},
                                {"role": "user", "content": message}
                            ],
                            max_tokens=300,
                            temperature=0.7
                        )
                        response = chat_response.choices[0].message.content
                    except AttributeError:
                        # إذا فشلت الواجهة الجديدة، جرب الواجهة القديمة
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

# Student Test Routes
@student_bp.route('/tests')
@login_required
def available_tests():
    """Show available tests for students"""
    # Get all active tests
    tests = Test.query.filter_by(is_active=True).all()
    
    # Get student's attempts for each test
    attempts_by_test = {}
    for test in tests:
        attempts = TestAttempt.query.filter_by(
            test_id=test.id,
            user_id=current_user.id
        ).order_by(TestAttempt.started_at.desc()).all()
        
        # Separate completed and in-progress attempts
        completed = [a for a in attempts if a.completed_at is not None]
        in_progress = [a for a in attempts if a.completed_at is None]
        
        attempts_by_test[test.id] = {
            'completed': completed,
            'in_progress': in_progress,
            'best_score': max([a.score for a in completed]) if completed else None
        }
    
    # إذا لم تكن هناك اختبارات، أنشئ اختبارًا تجريبيًا للاختبار
    if not tests:
        test = Test(
            title="اختبار الرياضيات الأساسية",
            description="اختبار أساسيات الرياضيات للصف الأول",
            created_by=1,  # افتراض أن المعرف 1 هو للمسؤول
            is_active=True,
            time_limit_minutes=30,
            passing_score=60
        )
        db.session.add(test)
        db.session.commit()
        
        # إضافة بعض الأسئلة للاختبار
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
            
        # إعادة الحصول على الاختبارات بعد إنشاء الاختبار الجديد
        tests = Test.query.filter_by(is_active=True).all()
        
        # تحديث attempts_by_test لتشمل الاختبار الجديد
        attempts_by_test[test.id] = {
            'completed': [],
            'in_progress': [],
            'best_score': None
        }
    
    return render_template('student/tests.html', 
                          tests=tests, 
                          attempts_by_test=attempts_by_test)

@student_bp.route('/tests/<int:test_id>/start', methods=['GET', 'POST'])
@login_required
def start_test(test_id):
    """Start a new test attempt"""
    test = Test.query.get_or_404(test_id)
    
    # Check if test is active
    if not test.is_active:
        flash('هذا الاختبار غير متاح حالياً.', 'warning')
        return redirect(url_for('student.available_tests'))
    
    # Check if there's already an in-progress attempt
    existing_attempt = TestAttempt.query.filter_by(
        test_id=test_id,
        user_id=current_user.id,
        completed_at=None
    ).first()
    
    if existing_attempt:
        # Resume existing attempt
        return redirect(url_for('student.take_test', attempt_id=existing_attempt.id))
    
    # Start new attempt
    form = TestAttemptForm()
    
    if form.validate_on_submit():
        # Create new attempt
        attempt = TestAttempt(
            test_id=test_id,
            user_id=current_user.id
        )
        db.session.add(attempt)
        db.session.commit()
        
        return redirect(url_for('student.take_test', attempt_id=attempt.id))
    
    return render_template('student/start_test.html', test=test, form=form)

@student_bp.route('/attempt/<int:attempt_id>/take', methods=['GET', 'POST'])
@login_required
def take_test(attempt_id):
    """Take a test"""
    attempt = TestAttempt.query.get_or_404(attempt_id)
    
    # Ensure this is the user's own attempt
    if attempt.user_id != current_user.id:
        abort(403)
    
    # If attempt is already completed, redirect to results
    if attempt.completed_at:
        return redirect(url_for('student.test_results', attempt_id=attempt_id))
    
    test = Test.query.get_or_404(attempt.test_id)
    
    # Check if time expired
    time_limit = timedelta(minutes=test.time_limit_minutes)
    time_elapsed = datetime.utcnow() - attempt.started_at
    time_remaining = time_limit - time_elapsed
    
    if time_remaining.total_seconds() <= 0:
        # Time expired, automatically submit
        attempt.completed_at = datetime.utcnow()
        attempt.calculate_score()
        db.session.commit()
        flash('انتهى وقت الاختبار وتم تسليمه تلقائياً.', 'info')
        return redirect(url_for('student.test_results', attempt_id=attempt_id))
    
    # Get all questions for this test
    questions = TestQuestion.query.filter_by(test_id=test.id).order_by(TestQuestion.order).all()
    
    # Create or get existing answers
    answers = {}
    for question in questions:
        answer = TestAnswer.query.filter_by(
            attempt_id=attempt.id,
            question_id=question.id
        ).first()
        
        if not answer:
            answer = TestAnswer(
                attempt_id=attempt.id,
                question_id=question.id
            )
            db.session.add(answer)
            db.session.commit()
        
        answers[question.id] = answer
    
    # Process form submission
    form = TestTakingForm()
    
    if form.validate_on_submit():
        action = request.form.get('action', '')
        
        # Process each question's answer
        for question in questions:
            field_name = f'question_{question.id}'
            if field_name in request.form:
                answer_value = request.form.get(field_name)
                
                if question.question_type == 'multiple_choice':
                    try:
                        choice_id = int(answer_value)
                        choice = QuestionChoice.query.get(choice_id)
                        
                        if choice and choice.question_id == question.id:
                            answer = answers[question.id]
                            answer.selected_choice_id = choice_id
                            answer.is_correct = choice.is_correct
                            db.session.commit()
                    except (ValueError, TypeError):
                        pass
                elif question.question_type == 'true_false':
                    try:
                        choice_id = int(answer_value)
                        choice = QuestionChoice.query.get(choice_id)
                        
                        if choice and choice.question_id == question.id:
                            answer = answers[question.id]
                            answer.selected_choice_id = choice_id
                            answer.is_correct = choice.is_correct
                            db.session.commit()
                    except (ValueError, TypeError):
                        pass
                elif question.question_type == 'short_answer':
                    answer = answers[question.id]
                    answer.text_answer = answer_value
                    # Short answer marking would need manual review or AI grading
                    db.session.commit()
        
        if action == 'submit':
            # Submit the test
            attempt.completed_at = datetime.utcnow()
            attempt.calculate_score()
            db.session.commit()
            flash('تم تسليم الاختبار بنجاح!', 'success')
            return redirect(url_for('student.test_results', attempt_id=attempt_id))
        else:
            # Save progress
            flash('تم حفظ إجاباتك.', 'success')
    
    # Calculate remaining time for JavaScript countdown
    seconds_remaining = int(time_remaining.total_seconds())
    
    return render_template('student/take_test.html',
                         test=test,
                         attempt=attempt,
                         questions=questions,
                         answers=answers,
                         seconds_remaining=seconds_remaining,
                         form=form)

@student_bp.route('/attempt/<int:attempt_id>/results')
@login_required
def test_results(attempt_id):
    """View results of a completed test"""
    attempt = TestAttempt.query.get_or_404(attempt_id)
    
    # Ensure this is the user's own attempt or an admin
    if attempt.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # If attempt is not completed yet, redirect to take test
    if not attempt.completed_at and attempt.user_id == current_user.id:
        return redirect(url_for('student.take_test', attempt_id=attempt_id))
    
    test = Test.query.get_or_404(attempt.test_id)
    
    # Calculate score if not already calculated
    if attempt.score is None:
        attempt.calculate_score()
        db.session.commit()
    
    # Get all questions and answers
    questions = TestQuestion.query.filter_by(test_id=test.id).order_by(TestQuestion.order).all()
    answers = TestAnswer.query.filter_by(attempt_id=attempt.id).all()
    
    # Organize answers by question_id for easier access in template
    answers_by_question = {answer.question_id: answer for answer in answers}
    
    return render_template('student/test_results.html',
                         test=test,
                         attempt=attempt,
                         questions=questions,
                         answers=answers_by_question)
