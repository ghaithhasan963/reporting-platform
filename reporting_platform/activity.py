from reporting_platform import db
from reporting_platform.app import Log
from datetime import datetime

def record_action(username, action):
    log = Log(username=username, action=action, timestamp=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
