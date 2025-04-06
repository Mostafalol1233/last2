"""
ملف لمهاجرة قاعدة البيانات وإضافة جدول test_retry_requests
"""
import os
from app import db, app
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from datetime import datetime

with app.app_context():
    # التحقق من وجود جدول test_retry_requests 
    inspector = db.inspect(db.engine)
    if 'test_retry_requests' not in inspector.get_table_names():
        meta = MetaData()
        
        test_retry_requests = Table(
            'test_retry_requests', meta,
            Column('id', Integer, primary_key=True),
            Column('test_id', Integer, ForeignKey('tests.id'), nullable=False),
            Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
            Column('request_date', DateTime, default=datetime.utcnow),
            Column('status', String(20), default='pending'),  # pending, approved, rejected, used
            Column('reason', Text, nullable=True),
            Column('admin_response', Text, nullable=True),
            Column('response_date', DateTime, nullable=True),
            Column('responded_by', Integer, ForeignKey('users.id'), nullable=True)
        )
        
        # إنشاء الجدول في قاعدة البيانات
        meta.create_all(db.engine)
        print("تم إنشاء جدول طلبات المحاولة الإضافية بنجاح")
    else:
        print("جدول طلبات المحاولة الإضافية موجود بالفعل")