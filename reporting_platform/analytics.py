from app import Report
from sqlalchemy import func
from reporting_platform import db

def get_reports_per_day():
    results = db.session.query(
        func.date(Report.created_at),
        func.count(Report.id)
    ).group_by(func.date(Report.created_at)).all()
    return results

def get_reports_by_location():
    results = db.session.query(
        func.round(Report.latitude, 2),
        func.round(Report.longitude, 2),
        func.count(Report.id)
    ).group_by(
        func.round(Report.latitude, 2),
        func.round(Report.longitude, 2)
    ).all()
    return results
