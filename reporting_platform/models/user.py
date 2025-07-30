from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # سيتم تشفيرها عند التسجيل

    role = db.Column(db.String(20), default='user')  # 'admin' أو 'user'
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='مبتدئ')  # مبتدئ / مساهم / مراقب / خبير

    # علاقات
    reports = db.relationship('Report', backref='owner', lazy=True)
    executions = db.relationship('Execution', backref='executor', lazy=True)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.full_name}, Role: {self.role}, Points: {self.points}>"
