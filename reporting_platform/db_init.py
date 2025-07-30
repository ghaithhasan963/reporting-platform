from reporting_platform import db
from reporting_platform.app import User, Report, Log, Comment

# بدء العملية
db.drop_all()    # إذا بدك تبدأ من الصفر
db.create_all()

# إضافة مستخدمين اختبار
test_user = User(username='ghaith_test', phone='0999999999', password='testpass', role='admin')
db.session.add(test_user)

# بلاغ اختبار
sample_report = Report(
    username='ghaith_test',
    category='خطاب كراهية',
    description='نص بلاغ اختباري',
    link='https://example.com',
    report_type='public',
    approved='approved',
    latitude=33.513,
    longitude=36.292
)
db.session.add(sample_report)

# تعليق اختبار
sample_comment = Comment(
    report_id=1,
    username='ghaith_test',
    text='تعليق تجريبي'
)
db.session.add(sample_comment)

# سجل نشاط
sample_log = Log(
    username='ghaith_test',
    action='إنشاء بلاغ اختباري'
)
db.session.add(sample_log)

db.session.commit()

print("📦 قاعدة البيانات جاهزة ✅")
