from app import app, db
from models import User, Video, Comment, Post, VideoView, LectureCode, VideoLike, StudentNote, AIChatMessage, DirectMessage
from werkzeug.security import generate_password_hash

# إعادة تهيئة قاعدة البيانات
def reinitialize_database():
    with app.app_context():
        # حذف كل الجداول الموجودة
        print("حذف الجداول الموجودة...")
        db.drop_all()
        
        # إعادة إنشاء الجداول
        print("إعادة إنشاء الجداول...")
        db.create_all()
        
        # إنشاء المستخدم المشرف الافتراضي
        print("إنشاء المستخدم المشرف الافتراضي...")
        admin = User(
            username='admin',
            full_name='مشرف النظام',
            email='admin@example.com',
            phone='1234567890',
            role='admin'
        )
        admin.set_password('admin123')
        
        # إنشاء حسابات طلاب افتراضية للاختبار
        student1 = User(
            username='student1',
            full_name='طالب للاختبار 1',
            email='student1@example.com',
            phone='0987654321',
            role='student'
        )
        student1.set_password('student123')
        
        student2 = User(
            username='student2',
            full_name='طالب للاختبار 2',
            email='student2@example.com',
            phone='1122334455',
            role='student'
        )
        student2.set_password('student123')
        
        # إضافة المستخدمين إلى قاعدة البيانات
        db.session.add(admin)
        db.session.add(student1)
        db.session.add(student2)
        
        # حفظ التغييرات
        db.session.commit()
        
        print("تم إعادة تهيئة قاعدة البيانات بنجاح!")
        print("حسابات المستخدمين الافتراضية:")
        print("- مشرف: اسم المستخدم: admin، كلمة المرور: admin123")
        print("- طالب: اسم المستخدم: student1، كلمة المرور: student123")
        print("- طالب: اسم المستخدم: student2، كلمة المرور: student123")

if __name__ == "__main__":
    reinitialize_database()