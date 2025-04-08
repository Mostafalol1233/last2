import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db_tables():
    """
    إنشاء جداول قاعدة البيانات في Neon PostgreSQL
    """
    # استخدام رابط قاعدة البيانات من متغير البيئة
    db_url = os.environ.get("DATABASE_URL", 
             "postgresql://lol_owner:npg_OyecuENlS45j@ep-broad-voice-a5mbecch-pooler.us-east-2.aws.neon.tech/lol?sslmode=require")
    
    if not db_url:
        logging.error("لم يتم توفير رابط قاعدة البيانات.")
        return False
    
    logging.info(f"استخدام قاعدة البيانات: {db_url}")
    
    try:
        # إنشاء تطبيق Flask مؤقت وقاعدة بيانات
        class Base(DeclarativeBase):
            pass
        
        db = SQLAlchemy(model_class=Base)
        app = Flask(__name__)
        
        # تكوين قاعدة البيانات
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
        
        db.init_app(app)
        
        with app.app_context():
            # استيراد النماذج
            import models
            
            # إنشاء الجداول
            db.create_all()
            logging.info("تم إنشاء جميع الجداول بنجاح")
            
            # التحقق من وجود مستخدمين
            from models import User
            admin_exists = db.session.query(User).filter_by(role='admin').first() is not None
            student_exists = db.session.query(User).filter_by(role='student').first() is not None
            
            if not admin_exists and not student_exists:
                logging.warning("لا يوجد مستخدمين في قاعدة البيانات")
                logging.info("جاري إنشاء المستخدمين الافتراضيين...")
                try:
                    from create_users import create_default_users
                    create_default_users()
                    logging.info("تم إنشاء المستخدمين الافتراضيين بنجاح")
                except Exception as e:
                    logging.error(f"فشل إنشاء المستخدمين الافتراضيين: {str(e)}")
            
            # إنشاء اختبار نموذجي
            try:
                from models import Test
                test_exists = db.session.query(Test).first() is not None
                
                if not test_exists:
                    logging.info("لا توجد اختبارات في قاعدة البيانات")
                    logging.info("جاري إنشاء اختبار نموذجي...")
                    try:
                        from create_test import create_sample_test
                        test = create_sample_test()
                        logging.info(f"تم إنشاء اختبار نموذجي: {test.title}")
                    except Exception as e:
                        logging.error(f"فشل إنشاء الاختبار النموذجي: {str(e)}")
            except Exception as e:
                logging.error(f"خطأ في التحقق من وجود اختبارات: {str(e)}")
        
        return True
        
    except Exception as e:
        logging.error(f"فشل إنشاء جداول قاعدة البيانات: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_db_tables()
    
    if success:
        print("\n✓ تم إنشاء وتهيئة قاعدة البيانات بنجاح!")
    else:
        print("\n✗ فشل تهيئة قاعدة البيانات. راجع رسائل الخطأ أعلاه.")