import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from models import User, Video, Comment, Post
from forms import LoginForm, VideoUploadForm, PostForm, CommentForm

# Create blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)
student_bp = Blueprint('student', __name__)

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

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# Admin routes
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        abort(403)
    
    videos = Video.query.order_by(Video.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/dashboard.html', videos=videos, posts=posts)

@admin_bp.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    if not current_user.is_admin():
        abort(403)
        
    form = VideoUploadForm()
    if form.validate_on_submit():
        video = Video(
            title=form.title.data,
            url=form.url.data,
            description=form.description.data,
            uploaded_by=current_user.id
        )
        db.session.add(video)
        db.session.commit()
        flash('Video uploaded successfully!', 'success')
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
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

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
        flash('Comment added successfully!', 'success')
        return redirect(url_for('student.view_video', video_id=video_id))
    
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
    return render_template('student/video.html', video=video, form=form, comments=comments)

@student_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('student/post.html', post=post)
