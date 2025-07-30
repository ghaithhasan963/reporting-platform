from models.report import Report
from sqlalchemy import func
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_reports_per_day():
    results = db.session.query(
        func.date(Report.created_at).label('day'),
        func.count(Report.id).label('count')
    ).group_by('day').order_by('day').all()

    return [{"day": str(r.day), "count": r.count} for r in results]


def get_reports_by_location():
    results = db.session.query(
        Report.location,
        func.count(Report.id).label('count')
    ).group_by(Report.location).order_by(func.count(Report.id).desc()).all()

    return [{"location": r.location, "count": r.count} for r in results]
