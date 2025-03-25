from app import app, db
from models import User

def create_default_users():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin', full_name='مسؤول النظام')
            admin.set_password('admin12345')
            db.session.add(admin)
            print("Admin user created")
        elif not admin.full_name:
            admin.full_name = 'مسؤول النظام'
            print("Admin full_name updated")
        
        # Check if student user already exists
        student = User.query.filter_by(username='student').first()
        if not student:
            student = User(username='student', role='student', full_name='طالب تجريبي')
            student.set_password('student12345')
            db.session.add(student)
            print("Student user created")
        elif not student.full_name:
            student.full_name = 'طالب تجريبي'
            print("Student full_name updated")
        
        db.session.commit()
        print("Default users created successfully!")

if __name__ == "__main__":
    create_default_users()