import os
import sys
import logging
import psycopg2
from psycopg2 import sql

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_database_schema():
    """
    إنشاء مخطط قاعدة البيانات في Neon PostgreSQL باستخدام SQL مباشرة
    """
    # استخدام رابط قاعدة البيانات من متغير البيئة
    db_url = os.environ.get("DATABASE_URL", 
             "postgresql://lol_owner:npg_OyecuENlS45j@ep-broad-voice-a5mbecch-pooler.us-east-2.aws.neon.tech/lol?sslmode=require")
    
    if not db_url:
        logging.error("لم يتم توفير رابط قاعدة البيانات.")
        return False
    
    logging.info(f"محاولة الاتصال بقاعدة البيانات: {db_url}")
    
    try:
        # إنشاء اتصال لقاعدة البيانات
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # التحقق من الاتصال
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        logging.info(f"تم الاتصال بنجاح: {db_version[0]}")
        
        # إنشاء جداول قاعدة البيانات
        create_tables_sql = """
        -- جدول المستخدمين
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(120),
            phone VARCHAR(20),
            password_hash VARCHAR(256) NOT NULL,
            role VARCHAR(20) NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول الفيديوهات
        CREATE TABLE IF NOT EXISTS video (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            url VARCHAR(255),
            file_path VARCHAR(255),
            description TEXT,
            uploaded_by INTEGER REFERENCES "user"(id),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            requires_code BOOLEAN DEFAULT TRUE,
            points_cost INTEGER DEFAULT 0
        );
        
        -- جدول أكواد الفيديو
        CREATE TABLE IF NOT EXISTS lecture_code (
            id SERIAL PRIMARY KEY,
            code VARCHAR(20) NOT NULL,
            video_id INTEGER REFERENCES video(id),
            created_by INTEGER REFERENCES "user"(id),
            student_id INTEGER REFERENCES "user"(id) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_used BOOLEAN DEFAULT FALSE,
            used_at TIMESTAMP NULL
        );
        
        -- جدول الملاحظات
        CREATE TABLE IF NOT EXISTS note (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول الاختبارات
        CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_limit_minutes INTEGER DEFAULT 30,
            passing_score INTEGER DEFAULT 60,
            is_active BOOLEAN DEFAULT TRUE,
            file_path VARCHAR(255),
            access_type VARCHAR(20) DEFAULT 'free',
            points_required INTEGER DEFAULT 0,
            access_code VARCHAR(50),
            max_attempts INTEGER DEFAULT 1
        );
        
        -- جدول أسئلة الاختبار
        CREATE TABLE IF NOT EXISTS test_question (
            id SERIAL PRIMARY KEY,
            test_id INTEGER REFERENCES test(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            points INTEGER DEFAULT 1,
            image_path VARCHAR(255)
        );
        
        -- جدول خيارات الأسئلة
        CREATE TABLE IF NOT EXISTS question_choice (
            id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES test_question(id) ON DELETE CASCADE,
            choice_text TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT FALSE
        );
        
        -- جدول محاولات الاختبار
        CREATE TABLE IF NOT EXISTS test_attempt (
            id SERIAL PRIMARY KEY,
            test_id INTEGER REFERENCES test(id),
            student_id INTEGER REFERENCES "user"(id),
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            score DECIMAL(5,2),
            is_passed BOOLEAN,
            points_earned INTEGER DEFAULT 0,
            attempt_number INTEGER DEFAULT 1
        );
        
        -- جدول إجابات الاختبار
        CREATE TABLE IF NOT EXISTS test_answer (
            id SERIAL PRIMARY KEY,
            attempt_id INTEGER REFERENCES test_attempt(id) ON DELETE CASCADE,
            question_id INTEGER REFERENCES test_question(id),
            selected_choice_id INTEGER REFERENCES question_choice(id),
            short_answer TEXT,
            is_correct BOOLEAN
        );
        
        -- جدول طلبات إعادة الاختبار
        CREATE TABLE IF NOT EXISTS test_retry_request (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES "user"(id),
            test_id INTEGER REFERENCES test(id),
            reason TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            admin_response TEXT,
            reviewed_by INTEGER REFERENCES "user"(id)
        );
        
        -- جدول المنشورات
        CREATE TABLE IF NOT EXISTS post (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول التعليقات
        CREATE TABLE IF NOT EXISTS comment (
            id SERIAL PRIMARY KEY,
            video_id INTEGER REFERENCES video(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES "user"(id),
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول الرسائل المباشرة
        CREATE TABLE IF NOT EXISTS direct_message (
            id SERIAL PRIMARY KEY,
            sender_id INTEGER REFERENCES "user"(id),
            recipient_id INTEGER REFERENCES "user"(id),
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMP
        );
        
        -- جدول سجلات مشاهدة الفيديو
        CREATE TABLE IF NOT EXISTS video_view (
            id SERIAL PRIMARY KEY,
            video_id INTEGER REFERENCES video(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES "user"(id),
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول سجلات النقاط
        CREATE TABLE IF NOT EXISTS point_transaction (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id),
            points INTEGER NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            reference_id INTEGER,
            reference_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        );
        
        -- جدول خطط الاشتراك
        CREATE TABLE IF NOT EXISTS subscription_plan (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'SAR',
            duration_days INTEGER NOT NULL,
            features TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- جدول اشتراكات المستخدمين
        CREATE TABLE IF NOT EXISTS user_subscription (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id),
            plan_id INTEGER REFERENCES subscription_plan(id),
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP NOT NULL,
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_reference VARCHAR(100),
            is_active BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # تنفيذ استعلام إنشاء الجداول
        cur.execute(create_tables_sql)
        conn.commit()
        logging.info("تم إنشاء الجداول بنجاح")
        
        # إنشاء مستخدم مشرف افتراضي إذا لم يكن موجوداً
        cur.execute("SELECT COUNT(*) FROM \"user\" WHERE role = 'admin'")
        admin_count = cur.fetchone()[0]
        
        if admin_count == 0:
            # إنشاء مستخدم مشرف افتراضي
            from werkzeug.security import generate_password_hash
            admin_password_hash = generate_password_hash('admin123')
            
            cur.execute(
                "INSERT INTO \"user\" (username, full_name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                ('admin', 'مدير النظام', 'admin@example.com', admin_password_hash, 'admin')
            )
            conn.commit()
            logging.info("تم إنشاء مستخدم مشرف افتراضي (اسم المستخدم: admin، كلمة المرور: admin123)")
        
        # إنشاء مستخدم طالب افتراضي إذا لم يكن موجوداً
        cur.execute("SELECT COUNT(*) FROM \"user\" WHERE role = 'student'")
        student_count = cur.fetchone()[0]
        
        if student_count == 0:
            # إنشاء مستخدم طالب افتراضي
            from werkzeug.security import generate_password_hash
            student_password_hash = generate_password_hash('student123')
            
            cur.execute(
                "INSERT INTO \"user\" (username, full_name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                ('student', 'طالب نموذجي', 'student@example.com', student_password_hash, 'student')
            )
            conn.commit()
            logging.info("تم إنشاء مستخدم طالب افتراضي (اسم المستخدم: student، كلمة المرور: student123)")
        
        # إغلاق الاتصال
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logging.error(f"فشل إنشاء قاعدة البيانات: {str(e)}")
        return False

if __name__ == "__main__":
    # تعيين متغير البيئة من وسيطة سطر الأوامر إذا تم توفيرها
    if len(sys.argv) > 1:
        os.environ["DATABASE_URL"] = sys.argv[1]
    
    success = create_database_schema()
    
    if success:
        print("\n✓ تم إنشاء وتهيئة قاعدة البيانات بنجاح!")
    else:
        print("\n✗ فشل تهيئة قاعدة البيانات. راجع رسائل الخطأ أعلاه.")