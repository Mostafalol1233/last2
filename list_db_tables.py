import os
import psycopg2

def list_tables():
    """
    عرض قائمة الجداول في قاعدة البيانات
    """
    try:
        db_url = os.environ.get("DATABASE_URL", 
                 "postgresql://neondb_owner:npg_BAjZRtCgi6F9@ep-raspy-dew-a6aotce0.us-west-2.aws.neon.tech/neondb?sslmode=require")
        
        # اتصال بقاعدة البيانات
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # استعلام عن الجداول الموجودة
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        print("\n== قائمة الجداول في قاعدة البيانات ==")
        if tables:
            for table in tables:
                print(f"- {table[0]}")
                
                # عرض الأعمدة في كل جدول
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table[0]}'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                if columns:
                    print("  الأعمدة:")
                    for col in columns:
                        print(f"    * {col[0]} ({col[1]})")
                
                # عرض عدد الصفوف في كل جدول
                try:
                    cur.execute(f"SELECT COUNT(*) FROM \"{table[0]}\";")
                    row_count = cur.fetchone()[0]
                    print(f"  عدد الصفوف: {row_count}")
                except Exception as e:
                    print(f"  خطأ في حساب عدد الصفوف: {str(e)}")
                
                print("  " + "-" * 30)
        else:
            print("لا توجد جداول في قاعدة البيانات")
        
        # إغلاق الاتصال
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

if __name__ == "__main__":
    list_tables()