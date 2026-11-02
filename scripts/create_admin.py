from getpass import getpass
from app import create_app
from app.extensions import db
from app.models import User, Department

app = create_app()
with app.app_context():
    db.create_all()
    email = input("Admin email: ").strip().lower()
    name = input("Admin full name: ").strip()
    password = getpass("Password (minimum 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Use at least 12 characters.")
    if User.query.filter_by(email=email).first():
        raise SystemExit("This email already exists.")
    admin = User(full_name=name, email=email, role="ADMIN")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Admin account created.")
