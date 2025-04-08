import os
import sys
import logging
import psycopg2

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_neon_connection():
    """
    اختبار الاتصال بقاعدة بيانات Neon PostgreSQL
    """
    # استخدام قيمة قاعدة البيانات من الوسيطة أو من متغير البيئة
    db_url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL")
    
    if not db_url:
        logging.error("لم يتم توفير رابط قاعدة البيانات. يرجى تمريره كوسيط أو تعيين متغير البيئة DATABASE_URL")
        return False
    
    logging.info(f"محاولة الاتصال بـ: {db_url}")
    
    try:
        # إنشاء اتصال لقاعدة البيانات
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # اختبار الاتصال بتنفيذ استعلام بسيط
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        
        # إغلاق الاتصال
        cur.close()
        conn.close()
        
        logging.info(f"تم الاتصال بنجاح: {db_version[0]}")
        return True
        
    except Exception as e:
        logging.error(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
        return False

if __name__ == "__main__":
    db_url = "postgresql://lol_owner:npg_OyecuENlS45j@ep-broad-voice-a5mbecch-pooler.us-east-2.aws.neon.tech/lol?sslmode=require"
    
    # تعيين متغير البيئة
    os.environ["DATABASE_URL"] = db_url
    
    # اختبار الاتصال
    success = test_neon_connection()
    
    if success:
        print("\n✓ تم الاتصال بقاعدة البيانات بنجاح!")
    else:
        print("\n✗ فشل الاتصال بقاعدة البيانات. راجع رسائل الخطأ أعلاه.")