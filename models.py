from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)  # الاسم الثلاثي
    email = db.Column(db.String(100), nullable=True)  # البريد الإلكتروني للاستعادة
    phone = db.Column(db.String(20), nullable=True)   # رقم الهاتف للاستعادة
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    points = db.Column(db.Integer, default=0)  # نقاط المحفظة
    reset_token = db.Column(db.String(100), nullable=True)  # رمز استعادة كلمة المرور
    reset_token_expiry = db.Column(db.DateTime, nullable=True)  # تاريخ انتهاء صلاحية الرمز
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ إنشاء الحساب
    
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
    points_cost = db.Column(db.Integer, default=0)  # تكلفة الفيديو بالنقاط
    
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
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # يمكن تعيين رمز لطالب محدد
    is_used = db.Column(db.Boolean, default=False)  # تم استخدام الرمز ام لا
    
    # العلاقات
    video = db.relationship('Video', backref=db.backref('access_codes', lazy='dynamic'))
    student = db.relationship('User', backref=db.backref('assigned_codes', lazy='dynamic'), foreign_keys=[assigned_to])
    
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

# إضافة نموذج الرسائل المباشرة بين المستخدمين
class DirectMessage(db.Model):
    __tablename__ = 'direct_messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات للوصول للمرسل والمستلم بسهولة
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_messages', lazy='dynamic'))

    def __repr__(self):
        return f'<DirectMessage {self.id} from {self.sender_id} to {self.recipient_id}>'

class PointTransfer(db.Model):
    __tablename__ = 'point_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة مع الطالب
    student = db.relationship('User', backref=db.backref('point_transfers', lazy='dynamic'))
    
    def __repr__(self):
        return f'<PointTransfer {self.points} points to student {self.student_id}>'

class PaymentPlan(db.Model):
    """Payment plan model for defining available plans"""
    __tablename__ = 'payment_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    features = db.Column(db.Text, nullable=True)  # JSON string of plan features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    stripe_price_id = db.Column(db.String(100), nullable=True)  # Stripe Price ID for this plan
    
    def set_features(self, features_list):
        """Store features list as JSON string"""
        self.features = json.dumps(features_list)
        
    def get_features(self):
        """Retrieve features as a list"""
        if self.features:
            return json.loads(self.features)
        return []
    
    def __repr__(self):
        return f'<PaymentPlan {self.name}: {self.price} {self.currency}>'

class Transaction(db.Model):
    """Transaction model for tracking payment transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('payment_plans.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    payment_processor = db.Column(db.String(20), nullable=False)  # stripe, paypal, etc.
    transaction_id = db.Column(db.String(100), nullable=True)  # External transaction ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    transaction_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional transaction data
    
    # Relationships
    user = db.relationship('User', backref=db.backref('transactions', lazy='dynamic'))
    plan = db.relationship('PaymentPlan', backref=db.backref('transactions', lazy='dynamic'))
    
    def set_metadata(self, data_dict):
        """Store dictionary as JSON string in transaction_metadata field"""
        self.transaction_metadata = json.dumps(data_dict)
        
    def get_metadata(self):
        """Retrieve transaction_metadata as dictionary"""
        if self.transaction_metadata:
            return json.loads(self.transaction_metadata)
        return {}
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} {self.currency} - {self.status}>'

class Subscription(db.Model):
    """User subscription model for tracking active subscriptions"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('payment_plans.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    auto_renew = db.Column(db.Boolean, default=False)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)  # Stripe Subscription ID
    payment_transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)  # Related payment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    plan = db.relationship('PaymentPlan', backref=db.backref('subscriptions', lazy='dynamic'))
    transaction = db.relationship('Transaction', backref=db.backref('subscriptions', lazy='dynamic'))
    
    def is_valid(self):
        """Check if subscription is currently valid"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now and self.end_date > now
    
    def __repr__(self):
        return f'<Subscription {self.id}: User {self.user_id} to Plan {self.plan_id}>'

class SMSMessage(db.Model):
    """SMS message model for tracking sent messages"""
    __tablename__ = 'sms_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional link to a user
    phone_number = db.Column(db.String(20), nullable=False)  # Recipient phone number
    message = db.Column(db.Text, nullable=False)  # Message content
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, sent, failed, delivered
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    external_id = db.Column(db.String(100), nullable=True)  # External ID (e.g., Twilio message ID)
    message_type = db.Column(db.String(50), nullable=True)  # Type of message (verification, notification, etc.)
    
    # Relationship to user (if applicable)
    user = db.relationship('User', backref=db.backref('sms_messages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SMSMessage {self.id} to {self.phone_number}: {self.status}>'

class Test(db.Model):
    """Model for educational tests/quizzes"""
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    time_limit_minutes = db.Column(db.Integer, default=30)  # Time limit in minutes
    passing_score = db.Column(db.Integer, default=60)  # Passing score percentage
    
    # Relationships
    questions = db.relationship('TestQuestion', backref='test', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('TestAttempt', backref='test', lazy='dynamic')
    creator = db.relationship('User', backref=db.backref('created_tests', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Test {self.id}: {self.title}>'

class TestQuestion(db.Model):
    """Model for test questions"""
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, short_answer
    points = db.Column(db.Integer, default=1)  # Points for this question
    order = db.Column(db.Integer, default=0)  # Order in the test
    image_path = db.Column(db.String(255), nullable=True)  # Path to question image
    
    # Relationships
    choices = db.relationship('QuestionChoice', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestQuestion {self.id} for Test {self.test_id}>'

class QuestionChoice(db.Model):
    """Model for multiple choice options"""
    __tablename__ = 'question_choices'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('test_questions.id'), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)  # Order of choices
    
    def __repr__(self):
        return f'<QuestionChoice {self.id} for Question {self.question_id}>'

class TestAttempt(db.Model):
    """Model for tracking test attempts by users"""
    __tablename__ = 'test_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)  # Final score as percentage
    passed = db.Column(db.Boolean, nullable=True)  # Whether the user passed
    
    # Relationships
    user = db.relationship('User', backref=db.backref('test_attempts', lazy='dynamic'))
    answers = db.relationship('TestAnswer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_score(self):
        """Calculate the score for this attempt"""
        if not self.completed_at:
            return None
            
        # Get total points available
        total_points = db.session.query(db.func.sum(TestQuestion.points)).filter(
            TestQuestion.test_id == self.test_id
        ).scalar() or 0
        
        if total_points == 0:
            return 0
            
        # Get points earned
        correct_answers = self.answers.filter_by(is_correct=True).all()
        points_earned = sum(answer.question.points for answer in correct_answers)
        
        # Calculate percentage
        percentage = (points_earned / total_points) * 100
        return round(percentage, 2)
    
    def __repr__(self):
        return f'<TestAttempt {self.id} by User {self.user_id} on Test {self.test_id}>'

class TestAnswer(db.Model):
    """Model for user answers to test questions"""
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('test_questions.id'), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey('question_choices.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)  # For short answer questions
    is_correct = db.Column(db.Boolean, nullable=True)
    
    # Relationships
    question = db.relationship('TestQuestion')
    selected_choice = db.relationship('QuestionChoice', foreign_keys=[selected_choice_id])
    
    def __repr__(self):
        return f'<TestAnswer {self.id} for Question {self.question_id} in Attempt {self.attempt_id}>'
        
class TestRetryRequest(db.Model):
    """نموذج لتتبع طلبات الطلاب لإعادة المحاولة في الاختبارات"""
    __tablename__ = 'test_retry_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reason = db.Column(db.Text, nullable=True)  # سبب طلب المحاولة الإضافية
    admin_response = db.Column(db.Text, nullable=True)  # رد المشرف على الطلب
    response_date = db.Column(db.DateTime, nullable=True)  # تاريخ الرد
    responded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # المشرف الذي رد على الطلب
    
    # Relationships
    test = db.relationship('Test', foreign_keys=[test_id])
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('retry_requests', lazy='dynamic'))
    admin = db.relationship('User', foreign_keys=[responded_by])
    
    def __repr__(self):
        return f'<TestRetryRequest {self.id} for Test {self.test_id}, User {self.user_id}, Status: {self.status}>'
