from main import app, db
from models import User

def add_student_user():
    with app.app_context():
        # Check if student user already exists
        existing_student = User.query.filter_by(username='student').first()
        if existing_student:
            print("مستخدم الطالب موجود بالفعل.")
            return
        
        # Create student user
        student = User(username='student', role='student', full_name='طالب تجريبي')
        student.set_password('student12345')
        db.session.add(student)
        
        db.session.commit()
        print("تم إضافة مستخدم الطالب بنجاح!")

if __name__ == "__main__":
    add_student_user()