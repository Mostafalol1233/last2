import os
import sys
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.sql import text

# تكوين الاتصال بقاعدة البيانات
# استخدام قاعدة بيانات SQLite محلية
DATABASE_URL = 'sqlite:///instance/app.db'

def migrate():
    """إضافة أعمدة خيارات الوصول إلى الاختبار في قاعدة البيانات."""
    engine = create_engine(DATABASE_URL)
    meta = MetaData()
    
    # التحقق من وجود الأعمدة
    with engine.connect() as conn:
        # التحقق من الجداول والأعمدة الموجودة
        inspector = meta.tables.get('tests', None)
        
        if inspector is None:
            # إذا كان الجدول غير موجود في الميتا داتا، نقوم بتحميله
            Table('tests', meta, autoload_with=engine)
            
        inspector = meta.tables.get('tests')
        
        columns_to_add = []
        
        if 'access_type' not in [c.name for c in inspector.columns]:
            columns_to_add.append("access_type VARCHAR(20) DEFAULT 'free'")
            
        if 'points_required' not in [c.name for c in inspector.columns]:
            columns_to_add.append("points_required INTEGER DEFAULT 0")
            
        if 'access_code' not in [c.name for c in inspector.columns]:
            columns_to_add.append("access_code VARCHAR(20) NULL")
            
        if columns_to_add:
            # إنشاء جملة SQL لإضافة الأعمدة
            for column_def in columns_to_add:
                alter_stmt = f"ALTER TABLE tests ADD COLUMN {column_def}"
                try:
                    conn.execute(text(alter_stmt))
                    print(f"تمت إضافة العمود: {column_def}")
                except Exception as e:
                    print(f"خطأ أثناء إضافة العمود {column_def}: {str(e)}")
            
            conn.commit()
            print("تمت إضافة أعمدة الوصول إلى الاختبار بنجاح!")
        else:
            print("جميع الأعمدة المطلوبة موجودة بالفعل.")

if __name__ == "__main__":
    try:
        migrate()
        print("اكتملت عملية الترحيل بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء الترحيل: {str(e)}")
        sys.exit(1)