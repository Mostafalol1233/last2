
from app import app, db
from models import User

def create_default_users():
    with app.app_context():
        # Update existing admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.set_password('Admin123@#')
            print("Admin password updated")
        else:
            admin = User(username='admin', role='admin', full_name='مسؤول النظام')
            admin.set_password('Admin123@#')
            db.session.add(admin)
            print("Admin user created")

        # Create second admin user
        admin2 = User.query.filter_by(username='admin2').first()
        if not admin2:
            admin2 = User(username='admin2', role='admin', full_name='مسؤول النظام 2')
            admin2.set_password('Admin123@#')
            db.session.add(admin2)
            print("Second admin user created")
        
        # Check if student user exists
        student = User.query.filter_by(username='student').first()
        if not student:
            student = User(username='student', role='student', full_name='طالب تجريبي')
            student.set_password('student12345')
            db.session.add(student)
            print("Student user created")
        
        db.session.commit()
        print("Users updated successfully!")

if __name__ == "__main__":
    create_default_users()
