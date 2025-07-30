from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    community_score = db.Column(db.Integer, default=0)  # تقييم من المجتمع
    achievement = db.Column(db.String(100))  # اسم الوسام أو الإنجاز

    user = db.relationship('User', backref='rewards')
