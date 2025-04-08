import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import importlib.util
import sys

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
        
        # تحميل ملف النماذج مباشرة لتجنب مشكلة الاستيراد الدائري
        def load_module_from_file(module_name, file_path):
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        
        # تحميل ملف النماذج
        models_module = load_module_from_file("db_models", "models.py")
        
        with app.app_context():
            # إنشاء الجداول
            db.create_all()
            logging.info("تم إنشاء جميع الجداول بنجاح")
            
            # التحقق من وجود مستخدمين
            User = getattr(models_module, "User")
            admin_exists = db.session.query(User).filter_by(role='admin').first() is not None
            student_exists = db.session.query(User).filter_by(role='student').first() is not None
            
            if not admin_exists and not student_exists:
                logging.warning("لا يوجد مستخدمين في قاعدة البيانات")
                logging.info("يمكنك إنشاء المستخدمين باستخدام create_users.py")
            
            # التحقق من وجود اختبارات
            try:
                Test = getattr(models_module, "Test")
                test_exists = db.session.query(Test).first() is not None
                
                if not test_exists:
                    logging.info("لا توجد اختبارات في قاعدة البيانات")
                    logging.info("يمكنك إنشاء اختبار نموذجي باستخدام create_test.py")
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