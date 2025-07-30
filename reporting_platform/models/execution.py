from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Execution(db.Model):
    __tablename__ = 'executions'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    executor_name = db.Column(db.String(100), nullable=False)
    execution_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='قيد التنفيذ')  # قيد التنفيذ / تم التنفيذ / ملغي

    notes = db.Column(db.Text)
    community_rating = db.Column(db.Integer, default=0)  # تقييم المجتمع 0-5

    report = db.relationship('Report', backref='executions')
