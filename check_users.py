import os
import logging
from main import app
from models import db, User, Video, Post

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_users_and_content():
    """
    عرض قائمة المستخدمين والفيديوهات والمنشورات الموجودة في قاعدة البيانات
    """
    with app.app_context():
        # عرض المستخدمين
        print("\n== قائمة المستخدمين ==")
        users = User.query.all()
        if users:
            for user in users:
                print(f"- اسم المستخدم: {user.username}")
                print(f"  الاسم الكامل: {user.full_name}")
                print(f"  الصلاحية: {user.role}")
                print(f"  البريد الإلكتروني: {user.email}")
                print(f"  النقاط: {user.points}")
                print("  " + "-" * 30)
        else:
            print("لا يوجد مستخدمين في قاعدة البيانات")
        
        # عرض الفيديوهات
        print("\n== قائمة الفيديوهات ==")
        videos = Video.query.all()
        if videos:
            for video in videos:
                uploader = User.query.get(video.uploaded_by) if video.uploaded_by else None
                print(f"- عنوان الفيديو: {video.title}")
                print(f"  الرابط: {video.url}")
                print(f"  الوصف: {video.description[:50]}..." if video.description and len(video.description) > 50 else f"  الوصف: {video.description}")
                print(f"  تم الرفع بواسطة: {uploader.username if uploader else 'غير معروف'}")
                print(f"  تاريخ الرفع: {video.upload_date}")
                print(f"  عدد المشاهدات: {video.views}")
                print("  " + "-" * 30)
        else:
            print("لا يوجد فيديوهات في قاعدة البيانات")
        
        # عرض المنشورات
        print("\n== قائمة المنشورات ==")
        posts = Post.query.all()
        if posts:
            for post in posts:
                author = User.query.get(post.author_id) if post.author_id else None
                print(f"- عنوان المنشور: {post.title}")
                print(f"  المحتوى: {post.content[:50]}..." if len(post.content) > 50 else f"  المحتوى: {post.content}")
                print(f"  الكاتب: {author.username if author else 'غير معروف'}")
                print(f"  تاريخ النشر: {post.created_at}")
                print("  " + "-" * 30)
        else:
            print("لا يوجد منشورات في قاعدة البيانات")

if __name__ == "__main__":
    try:
        list_users_and_content()
    except Exception as e:
        logging.error(f"خطأ: {str(e)}")