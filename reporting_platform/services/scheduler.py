from models.report import Report
from datetime import datetime, timedelta
from notifier import send_email, generate_notification
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def check_pending_reports():
    now = datetime.utcnow()
    deadline = now + timedelta(hours=24)

    reports = db.session.query(Report).filter(
        Report.status == "pending",
        Report.execution_deadline <= deadline
    ).all()

    for report in reports:
        user = report.user  # تأكد انه فيه علاقة بين Report و User
        body = generate_notification(user, "daily_reminder")
        send_email(user.email, "تذكير بتنفيذ البلاغ", body)
