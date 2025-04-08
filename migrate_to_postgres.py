import os
import sys
import logging
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تعريف مسارات قواعد البيانات
SQLITE_DB_PATH = os.path.join(os.getcwd(), 'instance', 'app.db')

# تعريف بيانات اتصال PostgreSQL
PG_HOST = os.environ.get('PGHOST', 'ep-wild-forest-a4zr1zo7-pooler.us-east-1.aws.neon.tech')
PG_PORT = os.environ.get('PGPORT', '5432')
PG_DATABASE = os.environ.get('PGDATABASE', 'neondb')
PG_USER = os.environ.get('PGUSER', 'neondb_owner')
PG_PASSWORD = os.environ.get('PGPASSWORD', 'npg_WqBr4uDCbNL8')
DATABASE_URL = os.environ.get('DATABASE_URL', f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}?sslmode=require')

# التحقق من وجود قاعدة بيانات SQLite
if not os.path.exists(SQLITE_DB_PATH):
    logging.error(f"قاعدة بيانات SQLite غير موجودة في المسار: {SQLITE_DB_PATH}")
    sys.exit(1)

def connect_to_sqlite():
    """إنشاء اتصال بقاعدة بيانات SQLite"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"خطأ في الاتصال بقاعدة بيانات SQLite: {e}")
        sys.exit(1)

def connect_to_postgres():
    """إنشاء اتصال بقاعدة بيانات PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.Error as e:
        logging.error(f"خطأ في الاتصال بقاعدة بيانات PostgreSQL: {e}")
        sys.exit(1)

def get_sqlite_tables(conn):
    """الحصول على قائمة الجداول في قاعدة بيانات SQLite"""
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row['name'] for row in cur.fetchall()]
    cur.close()
    return tables

def get_table_columns(sqlite_conn, table_name):
    """الحصول على أسماء الأعمدة لجدول محدد في قاعدة بيانات SQLite"""
    cur = sqlite_conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name});")
    columns = [row['name'] for row in cur.fetchall()]
    cur.close()
    return columns

def get_table_data(sqlite_conn, table_name):
    """الحصول على بيانات جدول محدد من قاعدة بيانات SQLite"""
    cur = sqlite_conn.cursor()
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    cur.close()
    return rows

def prepare_postgres_tables(pg_conn, sqlite_conn, tables):
    """إعداد الجداول في قاعدة بيانات PostgreSQL"""
    pg_cur = pg_conn.cursor()
    
    # تخزين الجداول التي تم إنشاؤها بنجاح
    created_tables = []
    
    for table_name in tables:
        try:
            # التحقق مما إذا كان الجدول موجوداً بالفعل
            pg_cur.execute(f"SELECT to_regclass('public.{table_name}');")
            table_exists = pg_cur.fetchone()[0] is not None
            
            if table_exists:
                logging.info(f"الجدول {table_name} موجود بالفعل في قاعدة بيانات PostgreSQL")
                created_tables.append(table_name)
                continue
            
            # جلب معلومات بنية الجدول من SQLite
            sqlite_cur = sqlite_conn.cursor()
            sqlite_cur.execute(f"PRAGMA table_info({table_name});")
            columns_info = sqlite_cur.fetchall()
            
            # إنشاء قائمة تعريفات الأعمدة
            column_definitions = []
            primary_keys = []
            
            for col in columns_info:
                col_name = col['name']
                col_type = col['type'].upper()
                
                # تحويل أنواع البيانات من SQLite إلى PostgreSQL
                if col_type == 'INTEGER':
                    pg_type = 'INTEGER'
                elif col_type == 'REAL':
                    pg_type = 'REAL'
                elif col_type.startswith('VARCHAR'):
                    length = col_type.split('(')[1].split(')')[0] if '(' in col_type else '255'
                    pg_type = f'VARCHAR({length})'
                elif col_type == 'TEXT':
                    pg_type = 'TEXT'
                elif col_type == 'BOOLEAN':
                    pg_type = 'BOOLEAN'
                elif col_type == 'DATETIME':
                    pg_type = 'TIMESTAMP'
                else:
                    pg_type = 'TEXT'  # نوع افتراضي
                
                # إضافة قيود NOT NULL و DEFAULT
                constraints = []
                if col['notnull'] == 1:
                    constraints.append('NOT NULL')
                
                if col['dflt_value'] is not None:
                    default_value = col['dflt_value']
                    
                    # معالجة القيم الافتراضية
                    if default_value.lower() == 'current_timestamp':
                        constraints.append("DEFAULT CURRENT_TIMESTAMP")
                    elif col_type == 'BOOLEAN':
                        if default_value.lower() in ('1', 'true'):
                            constraints.append("DEFAULT TRUE")
                        elif default_value.lower() in ('0', 'false'):
                            constraints.append("DEFAULT FALSE")
                    else:
                        constraints.append(f"DEFAULT {default_value}")
                
                # تحديد المفتاح الأساسي
                if col['pk'] == 1:
                    primary_keys.append(col_name)
                
                column_definitions.append(f"{col_name} {pg_type} {' '.join(constraints)}")
            
            # إضافة تعريف المفتاح الأساسي إذا كان موجوداً
            if primary_keys:
                column_definitions.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
            
            # إنشاء استعلام إنشاء الجدول
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    " + ",\n    ".join(column_definitions) + "\n);"
            logging.info(f"إنشاء جدول {table_name} في قاعدة بيانات PostgreSQL...")
            logging.debug(create_table_query)
            
            pg_cur.execute(create_table_query)
            created_tables.append(table_name)
            logging.info(f"تم إنشاء جدول {table_name} بنجاح")
            
            sqlite_cur.close()
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول {table_name}: {e}")
    
    pg_cur.close()
    return created_tables

def migrate_data(pg_conn, sqlite_conn, tables):
    """نقل البيانات من SQLite إلى PostgreSQL"""
    for table_name in tables:
        try:
            # جلب أسماء الأعمدة
            columns = get_table_columns(sqlite_conn, table_name)
            
            # جلب البيانات
            rows = get_table_data(sqlite_conn, table_name)
            
            if not rows:
                logging.info(f"لا توجد بيانات في جدول {table_name} لنقلها")
                continue
            
            logging.info(f"نقل {len(rows)} صف من جدول {table_name}...")
            
            pg_cur = pg_conn.cursor()
            
            # حذف البيانات الموجودة سابقاً في الجدول
            pg_cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
            
            # تحضير استعلام الإدراج
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # إدراج البيانات على دفعات
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                batch_values = [tuple(dict(row).values()) for row in batch]
                pg_cur.executemany(insert_query, batch_values)
                logging.info(f"تم نقل {min(i+batch_size, len(rows))}/{len(rows)} صف من جدول {table_name}")
            
            pg_cur.close()
            logging.info(f"تم نقل جميع البيانات من جدول {table_name} بنجاح")
        except Exception as e:
            logging.error(f"خطأ في نقل بيانات جدول {table_name}: {e}")

def reset_sequences(pg_conn, tables):
    """إعادة ضبط تسلسلات المفاتيح الأساسية في PostgreSQL"""
    pg_cur = pg_conn.cursor()
    
    for table_name in tables:
        try:
            # التحقق من وجود عمود id كمفتاح أساسي
            pg_cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'id'
            """)
            
            if pg_cur.fetchone():
                # إعادة ضبط تسلسل المفتاح الأساسي
                pg_cur.execute(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table_name}', 'id'), 
                        (SELECT MAX(id) FROM {table_name}), 
                        TRUE
                    );
                """)
                logging.info(f"تم إعادة ضبط تسلسل المفتاح الأساسي لجدول {table_name}")
        except Exception as e:
            logging.warning(f"خطأ في إعادة ضبط تسلسل جدول {table_name}: {e}")
    
    pg_cur.close()

def main():
    """الوظيفة الرئيسية لنقل البيانات"""
    logging.info("بدء عملية نقل البيانات من SQLite إلى PostgreSQL...")
    
    # الاتصال بقواعد البيانات
    sqlite_conn = connect_to_sqlite()
    pg_conn = connect_to_postgres()
    
    # الحصول على قائمة الجداول
    tables = get_sqlite_tables(sqlite_conn)
    logging.info(f"تم العثور على {len(tables)} جدول في قاعدة بيانات SQLite: {', '.join(tables)}")
    
    # إعداد الجداول في PostgreSQL
    created_tables = prepare_postgres_tables(pg_conn, sqlite_conn, tables)
    logging.info(f"تم إعداد {len(created_tables)} جدول في قاعدة بيانات PostgreSQL")
    
    # نقل البيانات
    migrate_data(pg_conn, sqlite_conn, created_tables)
    
    # إعادة ضبط تسلسلات المفاتيح الأساسية
    reset_sequences(pg_conn, created_tables)
    
    # إغلاق الاتصالات
    sqlite_conn.close()
    pg_conn.close()
    
    logging.info("تمت عملية نقل البيانات بنجاح")

if __name__ == "__main__":
    main()