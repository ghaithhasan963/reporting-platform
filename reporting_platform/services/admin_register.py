import os
from models.user import User
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_admin():
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    rank = os.getenv("ADMIN_RANK", "مدير عام")

    if not db.session.query(User).filter_by(username=username).first():
        hashed_pw = generate_password_hash(password)
        new_admin = User(username=username, password=hashed_pw, role="admin", rank=rank)
        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ تم إنشاء إداري باسم: {username}")
    else:
        print("⚠️ الإداري موجود بالفعل.")
