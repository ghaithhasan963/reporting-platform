from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(150), nullable=False)  # عنوان مختصر
    description = db.Column(db.Text, nullable=False)    # وصف البلاغ
    image_path = db.Column(db.String(250))              # مسار الصورة
    location = db.Column(db.String(250), nullable=False) # الموقع الجغرافي

    category = db.Column(db.String(50))                 # الفئة المقترحة (من التصنيف الذكي)
    auto_classified = db.Column(db.Boolean, default=False)  # هل تم تصنيفها تلقائيًا؟

    status = db.Column(db.String(20), default='بانتظار المعالجة')  # حالات: قيد الانتظار، مقبول، مرفوض، منفذ
    scheduled_at = db.Column(db.DateTime)               # تاريخ التنفيذ المجدول

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # تقييم المجتمع
    community_score = db.Column(db.Integer, default=0)  # نقاط التصويت
    votes_count = db.Column(db.Integer, default=0)

    # علاقات
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executions = db.relationship('Execution', backref='report', lazy=True)

    def __repr__(self):
        return f"<Report {self.title}, Status: {self.status}, Category: {self.category}>"
