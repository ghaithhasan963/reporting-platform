import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.report import Report
from models.execution import Execution
from models.reward import Reward

db = SQLAlchemy()

def init_app():
    app = Flask(__name__)

    # قاعدة البيانات: SQLite محلي أو PostgreSQL إنتاجي
    db_uri = os.getenv('DATABASE_URL', 'sqlite:///savnet.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # حماية الجلسة عبر مفتاح بيئي
    app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

    # ربط المكتبة
    db.init_app(app)

    # إنشاء الجداول داخل السياق
    with app.app_context():
        db.create_all()
        print("✅ تم إنشاء قاعدة البيانات والجداول بنجاح!")

    return app
