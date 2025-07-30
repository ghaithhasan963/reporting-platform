from flask import session
from datetime import datetime
import smtplib

def generate_notification(user, event_type):
    if event_type == "report_submitted":
        return f"شكرًا يا {user.name}! تم استلام بلاغك بنجاح 🛡️"
    elif event_type == "report_executed":
        return f"🎉 تم تنفيذ البلاغ الذي قدمته! راجع التفاصيل."
    elif event_type == "daily_reminder":
        return f"صباح الخير، لا تنسَ متابعة تنفيذاتك وإضافة تقييماتك اليوم 🌞"
    return ""

def send_email(to_email, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_app_password")
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail("your_email@gmail.com", to_email, message)
        server.quit()
    except Exception as e:
        print(f"فشل إرسال البريد: {e}")
