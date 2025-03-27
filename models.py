from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)  # الاسم الثلاثي
    email = db.Column(db.String(100), nullable=True)  # البريد الإلكتروني للاستعادة
    phone = db.Column(db.String(20), nullable=True)   # رقم الهاتف للاستعادة
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    reset_token = db.Column(db.String(100), nullable=True)  # رمز استعادة كلمة المرور
    reset_token_expiry = db.Column(db.DateTime, nullable=True)  # تاريخ انتهاء صلاحية الرمز
    
    # Relationships
    videos = db.relationship('Video', backref='uploader', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    video_views = db.relationship('VideoView', backref='viewer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def generate_reset_token(self):
        """توليد رمز استعادة كلمة المرور وتاريخ انتهاء صلاحيته (24 ساعة)"""
        import secrets
        from datetime import datetime, timedelta
        self.reset_token = secrets.token_hex(16)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        return self.reset_token
    
    def check_reset_token(self, token):
        """التحقق من صلاحية رمز استعادة كلمة المرور"""
        from datetime import datetime
        if self.reset_token != token:
            return False
        if self.reset_token_expiry < datetime.utcnow():
            return False
        return True
        
    def __repr__(self):
        return f'<User {self.username}>'

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=True)  # يمكن أن يكون فارغًا في حالة رفع ملف
    file_path = db.Column(db.String(200), nullable=True)  # مسار الملف المرفوع
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requires_code = db.Column(db.Boolean, default=True)  # هل تتطلب المحاضرة كود للوصول
    
    # Relationships
    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Video {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment by {self.user_id} on Video {self.video_id}>'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.title}>'

class VideoView(db.Model):
    __tablename__ = 'video_views'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the video
    video = db.relationship('Video', backref=db.backref('views', lazy='dynamic'))
    
    def __repr__(self):
        return f'<VideoView by {self.user_id} on Video {self.video_id}>'

class LectureCode(db.Model):
    __tablename__ = 'lecture_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to the video
    video = db.relationship('Video', backref=db.backref('access_codes', lazy='dynamic'))
    
    def __repr__(self):
        return f'<LectureCode {self.code} for Video {self.video_id}>'

# إضافة نموذج الإعجابات (اللايك)
class VideoLike(db.Model):
    __tablename__ = 'video_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات مع الجداول الأخرى
    video = db.relationship('Video', backref=db.backref('likes', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('liked_videos', lazy='dynamic'))
    
    # ضمان أن كل مستخدم يمكنه عمل لايك واحد فقط لكل فيديو
    __table_args__ = (db.UniqueConstraint('video_id', 'user_id', name='_video_user_like_uc'),)
    
    def __repr__(self):
        return f'<VideoLike by User {self.user_id} on Video {self.video_id}>'

# إضافة نموذج الملاحظات الشخصية
class StudentNote(db.Model):
    __tablename__ = 'student_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('notes', lazy='dynamic'))
    
    def __repr__(self):
        return f'<StudentNote {self.id} by User {self.user_id}: {self.title}>'

# إضافة نموذج رسائل الدردشة الذكية
class AIChatMessage(db.Model):
    __tablename__ = 'ai_chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('ai_chat_messages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AIChatMessage {self.id} by User {self.user_id}>'
