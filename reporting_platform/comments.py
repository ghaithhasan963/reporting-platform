from app import db, Comment
from datetime import datetime

def add_comment(report_id, username, text):
    c = Comment(report_id=report_id, username=username, text=text, timestamp=datetime.utcnow())
    db.session.add(c)
    db.session.commit()

def get_comments(report_id):
    return Comment.query.filter_by(report_id=report_id).order_by(Comment.timestamp.desc()).all()
