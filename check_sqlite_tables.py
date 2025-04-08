import sqlite3
import os

def check_sqlite_tables():
    """
    عرض قائمة الجداول في قاعدة بيانات SQLite
    """
    sqlite_db = "app.db"
    
    if not os.path.exists(sqlite_db):
        print(f"ملف قاعدة بيانات SQLite غير موجود: {sqlite_db}")
        return
    
    try:
        # اتصال بقاعدة بيانات SQLite
        conn = sqlite3.connect(sqlite_db)
        cursor = conn.cursor()
        
        # استعلام عن الجداول الموجودة
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n== قائمة الجداول في قاعدة بيانات SQLite ==")
        if tables:
            for table in tables:
                print(f"- {table[0]}")
                
                # عرض الأعمدة في كل جدول
                try:
                    cursor.execute(f"PRAGMA table_info({table[0]});")
                    columns = cursor.fetchall()
                    if columns:
                        print("  الأعمدة:")
                        for col in columns:
                            col_name = col[1]
                            col_type = col[2]
                            print(f"    * {col_name} ({col_type})")
                    
                    # عرض عدد الصفوف في كل جدول
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table[0]}\";")
                    row_count = cursor.fetchone()[0]
                    print(f"  عدد الصفوف: {row_count}")
                    print("  " + "-" * 30)
                except Exception as e:
                    print(f"  خطأ في الحصول على معلومات الجدول {table[0]}: {str(e)}")
        else:
            print("لا توجد جداول في قاعدة البيانات")
        
        # إغلاق الاتصال
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

if __name__ == "__main__":
    check_sqlite_tables()