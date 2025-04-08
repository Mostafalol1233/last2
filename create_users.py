
from main import app, db
from models import User

def create_default_users():
    with app.app_context():
        # Delete all existing users
        User.query.delete()

        # Create first admin user
        admin = User(username='admin', role='admin', full_name='مسؤول النظام')
        admin.set_password('ahmedhelly123@#')
        db.session.add(admin)
        print("Admin user created")

        # Create second admin user
        admin2 = User(username='admin2', role='admin', full_name='مسؤول النظام 2')
        admin2.set_password('ahmedhelly123@#')
        db.session.add(admin2)
        print("Second admin user created")

        # Create security admin
        security = User(username='security', role='admin', full_name='مسؤول الأمن')
        security.set_password('ahmedhelly123@#')
        db.session.add(security)
        print("Security admin user created")

        # Create ahmedhelly user
        ahmedhelly = User(username='ahmedhelly', role='admin', full_name='أحمد حلي')
        ahmedhelly.set_password('ahmedhelly123@#')
        db.session.add(ahmedhelly)
        print("AhmedHelly admin user created")

        # Create student user
        student = User(username='student', role='student', full_name='طالب تجريبي')
        student.set_password('student12345')
        db.session.add(student)
        print("Student user created")

        db.session.commit()
        print("Users updated successfully!")

if __name__ == "__main__":
    create_default_users()
