from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from report_analytics import get_reports_per_day, get_reports_by_location
from activity import record_action
from alerts import is_nearby
from comments import add_comment, get_comments
from rating import rate_report

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", "savenet_secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

# 🧑 نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='جديد 🐣')

# 📨 نموذج البلاغ
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    link = db.Column(db.String(250))
    report_type = db.Column(db.String(20), default='private')
    approved = db.Column(db.String(20), default='pending')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=0)

# 📝 نموذج النشاط
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 🗒️ نموذج التعليق
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 👋 صفحة الترحيب
@app.route('/')
def welcome():
    if 'user' in session: return redirect('/explore')
    return render_template('welcome.html')

# 🧾 تسجيل حساب
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        if User.query.filter_by(username=u).first():
            return render_template('register.html', error="الاسم مستخدم مسبقاً.")
        pw = generate_password_hash(request.form['password'])
        new_user = User(username=u, phone=request.form['phone'], password=pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# 🔐 تسجيل دخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p):
            session['user'] = user.username
            session['role'] = user.role
            return redirect('/dashboard') if user.role == 'user' else redirect('/admin_dashboard')
        return render_template('login.html', error=True)
    return render_template('login.html')

# ⏏️ تسجيل خروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 📨 رفع بلاغ
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session: return redirect('/login')
    if request.method == 'POST':
        r = Report(
            username=session['user'],
            category=request.form['category'],
            description=request.form['description'],
            link=request.form['link'],
            report_type=request.form['report_type'],
            latitude=request.form.get('latitude'),
            longitude=request.form.get('longitude')
        )
        db.session.add(r)
        db.session.commit()
        # تسجيل النشاط
        log = Log(username=session['user'], action='رفع بلاغ')
        db.session.add(log)
        db.session.commit()
        return render_template('submit_report.html', success=True)
    return render_template('submit_report.html')

# 👤 الملف الشخصي
@app.route('/profile')
def profile():
    if 'user' not in session: return redirect('/login')
    u = User.query.filter_by(username=session['user']).first()
    reports = Report.query.filter_by(username=u.username).all()
    approved_reports = [r for r in reports if r.approved == 'approved']
    level = ('خبير 🔥' if len(approved_reports) >= 50 else 'نشط 💪' if len(approved_reports) >= 20 else 'مشارك 🤝' if len(approved_reports) >= 5 else 'جديد 🐣')
    u.level = level
    db.session.commit()
    return render_template('profile.html', user=u, reports=reports, level=level)

# 🏠 لوحة المستخدم
@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    reports = Report.query.filter_by(username=session['user']).all()
    return render_template('dashboard.html', reports=reports)

# 🛡️ لوحة الأدمن
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
    users = User.query.all()
    pending_reports = Report.query.filter_by(approved='pending').all()
    stats = db.session.query(Report.category, db.func.count(Report.category))\
        .group_by(Report.category).all()
    user_summary = []
    for u in users:
        total = Report.query.filter_by(username=u.username).count()
        approved = Report.query.filter_by(username=u.username, approved='approved').count()
        level = ('خبير 🔥' if approved >= 50 else 'نشط 💪' if approved >= 20 else 'مشارك 🤝' if approved >= 5 else 'جديد 🐣')
        user_summary.append({
            'username': u.username,
            'phone': u.phone,
            'role': u.role,
            'reports': total,
            'approved': approved,
            'level': level
        })
    return render_template('admin_dashboard.html', users=user_summary, pending=pending_reports, stats=stats)

# ✅ قبول بلاغ وزيادة نقاط المستخدم
@app.route('/approve/<int:id>')
def approve(id):
    r = Report.query.get(id)
    r.approved = 'approved'
    db.session.commit()
    user = User.query.filter_by(username=r.username).first()
    user.score += 10
    db.session.commit()
    return redirect('/admin_dashboard')

# ❌ رفض بلاغ
@app.route('/reject/<int:id>')
def reject(id):
    r = Report.query.get(id)
    r.approved = 'rejected'
    db.session.commit()
    return redirect('/admin_dashboard')

# 💬 تقييم بلاغ
@app.route('/rate/<int:id>')
def rate(id):
    r = Report.query.get(id)
    r.rating += 1
    db.session.commit()
    return redirect('/explore')

# 🗺️ عرض البلاغات على الخريطة
@app.route('/alerts_map')
def alerts_map():
    reports = Report.query.filter(Report.latitude != None, Report.longitude != None).all()
    return render_template('alerts_map.html', reports=reports)

# 📥 استكشاف البلاغات
@app.route('/explore')
def explore():
    reports = Report.query.filter_by(approved='approved').all()
    return render_template('reports_feed.html', reports=reports)

# 🧭 تشغيل السيرفر
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
