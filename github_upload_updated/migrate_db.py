from app import app, db
from models import TestQuestion
import sqlite3
import os

def add_image_path_column():
    # مسار قاعدة البيانات ثابت
    db_path = 'instance/app.db'
    
    if not os.path.exists(db_path):
        print(f"قاعدة البيانات غير موجودة في المسار: {db_path}")
        return
    
    # فتح اتصال مباشر بقاعدة البيانات
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # التحقق مما إذا كان العمود موجوداً بالفعل
        cursor.execute("PRAGMA table_info(test_questions)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'image_path' not in column_names:
            # إضافة العمود الجديد
            cursor.execute("ALTER TABLE test_questions ADD COLUMN image_path TEXT")
            conn.commit()
            print("تم إضافة عمود image_path بنجاح")
            
            # تحديث القيمة للسؤال الخامس
            cursor.execute("UPDATE test_questions SET image_path = ? WHERE id = ?", ('img/tests/question5.png', 5))
            conn.commit()
            print("تم تحديث قيمة الصورة للسؤال رقم 5")
        else:
            print("العمود image_path موجود بالفعل")
            
            # تحديث القيمة للسؤال الخامس
            cursor.execute("UPDATE test_questions SET image_path = ? WHERE id = ?", ('img/tests/question5.png', 5))
            conn.commit()
            print("تم تحديث قيمة الصورة للسؤال رقم 5")
    
    except Exception as e:
        print(f"حدث خطأ: {e}")
    finally:
        # إغلاق الاتصال
        conn.close()

if __name__ == "__main__":
    add_image_path_column()