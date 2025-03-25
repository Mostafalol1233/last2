import logging
import os
import secrets
import string
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from app import db
from models import User, Video, Comment, Post, VideoView, LectureCode
from forms import (
    LoginForm, VideoUploadForm, PostForm, CommentForm, RegistrationForm,
    LectureCodeForm, GenerateCodeForm
)

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
    # تحديد الدور للمستخدم كطالب فقط، لا يمكن إنشاء حسابات بصلاحيات مسؤول عن طريق التسجيل
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            role='student',  # دائمًا نجعل المستخدم المسجل طالبًا وليس مسؤولًا
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('تم تسجيل الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('main.login'))
    
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

@admin_bp.route('/generate_lecture_code/<int:video_id>', methods=['POST'])
@login_required
def create_lecture_code(video_id):
    if not current_user.is_admin():
        abort(403)
        
    video = Video.query.get_or_404(video_id)
    
    # توليد كود جديد
    code = generate_random_code()
    lecture_code = LectureCode(
        video_id=video.id,
        code=code,
        is_active=True
    )
    db.session.add(lecture_code)
    db.session.commit()
    
    flash(f'تم إنشاء كود جديد للمحاضرة: {code}', 'success')
    return redirect(url_for('admin.dashboard'))

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

# Student routes
@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
        
    videos = Video.query.order_by(Video.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('student/dashboard.html', videos=videos, posts=posts)

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
            lecture_code = LectureCode.query.filter_by(
                video_id=video_id, 
                code=code, 
                is_active=True
            ).first()
        
        if lecture_code:
            # الكود صحيح، تسجيل المشاهدة
            view = VideoView(
                video_id=video_id,
                user_id=current_user.id
            )
            db.session.add(view)
            db.session.commit()
            flash('تم التحقق من الكود بنجاح!', 'success')
            return redirect(url_for('student.view_video', video_id=video_id))
        else:
            flash('الكود غير صحيح أو غير نشط. يرجى المحاولة مرة أخرى.', 'danger')
    
    return render_template('student/enter_lecture_code.html', form=form, video=video)

@student_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('student/post.html', post=post)
