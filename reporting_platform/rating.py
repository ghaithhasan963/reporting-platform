from reporting_platform.app import db, Report

def rate_report(report_id, value=1):
    r = Report.query.get(report_id)
    if r:
        r.rating += value
        db.session.commit()
