import os
import logging
import psycopg2
from psycopg2 import sql
import sqlite3
from datetime import datetime

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def import_data_from_sqlite():
    """
    استيراد البيانات من قاعدة بيانات SQLite إلى PostgreSQL
    """
    # رابط قاعدة بيانات PostgreSQL
    pg_url = os.environ.get("DATABASE_URL", 
            "postgresql://neondb_owner:npg_BAjZRtCgi6F9@ep-raspy-dew-a6aotce0.us-west-2.aws.neon.tech/neondb?sslmode=require")
    
    # رابط قاعدة بيانات SQLite
    sqlite_db = "app.db"
    
    if not os.path.exists(sqlite_db):
        logging.error(f"ملف قاعدة بيانات SQLite غير موجود: {sqlite_db}")
        return False
    
    try:
        # اتصال بقاعدة بيانات SQLite
        sqlite_conn = sqlite3.connect(sqlite_db)
        sqlite_cursor = sqlite_conn.cursor()
        
        # اتصال بقاعدة بيانات PostgreSQL
        pg_conn = psycopg2.connect(pg_url)
        pg_cursor = pg_conn.cursor()
        
        # 1. استيراد المستخدمين
        logging.info("استيراد بيانات المستخدمين...")
        sqlite_cursor.execute("SELECT id, username, email, password_hash, role, full_name, phone, points FROM user")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            user_id, username, email, password_hash, role, full_name, phone, points = user
            
            # التحقق من وجود المستخدم
            pg_cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            existing_user = pg_cursor.fetchone()
            
            if existing_user:
                logging.info(f"المستخدم موجود بالفعل: {username}")
                continue
            
            # إضافة المستخدم الجديد
            pg_cursor.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, full_name, phone, points) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, username, email, password_hash, role or 'student', full_name, phone, points or 0)
            )
        
        # 2. استيراد الفيديوهات
        logging.info("استيراد بيانات الفيديوهات...")
        sqlite_cursor.execute("SELECT id, title, url, file_path, description, uploaded_by, upload_date, views, requires_code, points_cost FROM video")
        videos = sqlite_cursor.fetchall()
        
        for video in videos:
            video_id, title, url, file_path, description, uploaded_by, upload_date, views, requires_code, points_cost = video
            
            # التحقق من وجود الفيديو
            pg_cursor.execute(
                "SELECT id FROM videos WHERE title = %s AND url = %s",
                (title, url)
            )
            existing_video = pg_cursor.fetchone()
            
            if existing_video:
                logging.info(f"الفيديو موجود بالفعل: {title}")
                continue
            
            # إضافة الفيديو الجديد
            pg_cursor.execute(
                """
                INSERT INTO videos (id, title, url, file_path, description, uploaded_by, upload_date, views, requires_code, points_cost) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    video_id, 
                    title, 
                    url, 
                    file_path, 
                    description, 
                    uploaded_by, 
                    upload_date or datetime.now(), 
                    views or 0, 
                    requires_code or True, 
                    points_cost or 0
                )
            )
        
        # 3. استيراد المنشورات
        logging.info("استيراد بيانات المنشورات...")
        sqlite_cursor.execute("SELECT id, title, content, created_by, created_at FROM post")
        posts = sqlite_cursor.fetchall()
        
        for post in posts:
            post_id, title, content, created_by, created_at = post
            
            # التحقق من وجود المنشور
            pg_cursor.execute(
                "SELECT id FROM posts WHERE title = %s AND created_by = %s",
                (title, created_by)
            )
            existing_post = pg_cursor.fetchone()
            
            if existing_post:
                logging.info(f"المنشور موجود بالفعل: {title}")
                continue
            
            # إضافة المنشور الجديد
            pg_cursor.execute(
                """
                INSERT INTO posts (id, title, content, created_by, created_at) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    post_id, 
                    title, 
                    content, 
                    created_by, 
                    created_at or datetime.now()
                )
            )
        
        # 4. استيراد الاختبارات
        logging.info("استيراد بيانات الاختبارات...")
        sqlite_cursor.execute("SELECT id, title, description, created_by, created_at, is_active, time_limit_minutes, passing_score, max_attempts FROM test")
        tests = sqlite_cursor.fetchall()
        
        for test in tests:
            test_id, title, description, created_by, created_at, is_active, time_limit_minutes, passing_score, max_attempts = test
            
            # التحقق من وجود الاختبار
            pg_cursor.execute(
                "SELECT id FROM tests WHERE title = %s AND created_by = %s",
                (title, created_by)
            )
            existing_test = pg_cursor.fetchone()
            
            if existing_test:
                logging.info(f"الاختبار موجود بالفعل: {title}")
                continue
            
            # إضافة الاختبار الجديد
            pg_cursor.execute(
                """
                INSERT INTO tests (id, title, description, created_by, created_at, is_active, time_limit_minutes, passing_score, max_attempts) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    test_id, 
                    title, 
                    description, 
                    created_by, 
                    created_at or datetime.now(), 
                    is_active or True, 
                    time_limit_minutes or 30, 
                    passing_score or 60,
                    max_attempts or 1
                )
            )
        
        # حفظ التغييرات
        pg_conn.commit()
        
        # إغلاق الاتصالات
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()
        
        logging.info("تم استيراد البيانات بنجاح")
        return True
        
    except Exception as e:
        logging.error(f"خطأ أثناء استيراد البيانات: {str(e)}")
        return False

if __name__ == "__main__":
    if import_data_from_sqlite():
        print("\n✓ تم استيراد البيانات بنجاح!")
    else:
        print("\n✗ فشل استيراد البيانات. راجع سجلات الأخطاء أعلاه.")