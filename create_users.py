from app import app, db
from models import User

def create_default_users():
    with app.app_context():
        # Delete all existing users
        User.query.delete()

        # Create first admin user
        admin = User(username='admin', role='admin', full_name='مسؤول النظام')
        admin.set_password('Admin123@#')
        db.session.add(admin)
        print("Admin user created")

        # Create second admin user
        admin2 = User(username='admin2', role='admin', full_name='مسؤول النظام 2')
        admin2.set_password('Ahmedhelly')
        db.session.add(admin2)
        print("Second admin user created")

        # Create security admin
        security = User(username='security', role='admin', full_name='مسؤول الأمن')
        security.set_password('Security@123')
        db.session.add(security)
        print("Security admin user created")

        db.session.commit()
        print("Users updated successfully!")

if __name__ == "__main__":
    create_default_users()