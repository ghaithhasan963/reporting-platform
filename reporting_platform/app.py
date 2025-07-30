from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# 👤 المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(50))
    role = db.Column(db.String(10), default='user')

# 📝 البلاغ
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    link = db.Column(db.String(250))
    report_type = db.Column(db.String(20), default='private')
    approved = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 🏠 الصفحة الترحيبية
@app.route('/')
def welcome():
    return render_template('welcome.html')

# 📊 الصفحة العامة للبلاغات
@app.route('/explore')
def explore():
    published = Report.query.filter_by(approved='approved').all()
    return render_template('explore.html', reports=published)

# 🔐 تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user'] = u
            session['role'] = user.role
            return redirect('/admin_dashboard' if user.role == 'admin' else '/dashboard')
        return render_template('login.html', error=True)
    return render_template('login.html')

# 📝 التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form.get('confirm'):
            return render_template('register.html', mismatch=True)
        user = User(username=request.form['username'], phone=request.form['phone'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# 📤 رفع البلاغ
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session: return redirect('/login')
    if request.method == 'POST':
        r = Report(
            username=session['user'],
            category=request.form['category'],
            description=request.form['description'],
            link=request.form['link'],
            report_type=request.form['report_type']
        )
        db.session.add(r)
        db.session.commit()
        return render_template('submit_report.html', success=True)
    return render_template('submit_report.html')

# 👤 الملف الشخصي
@app.route('/profile')
def profile():
    if 'user' not in session: return redirect('/login')
    user = User.query.filter_by(username=session['user']).first()
    reports = Report.query.filter_by(username=session['user']).all()
    approved = len([r for r in reports if r.approved == 'approved'])
    level = (
        'خبير 🔥' if approved >= 50 else
        'نشط 💪' if approved >= 20 else
        'مشارك 🤝' if approved >= 5 else
        'جديد 🐣'
    )
    return render_template('profile.html', user=user, reports=reports, level=level)

# 🛡️ لوحة الأدمن
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin': return redirect('/login')
    users = User.query.all()
    pending = Report.query.filter_by(approved='pending').all()
    frequent = db.session.query(
        Report.category, db.func.count(Report.category)
    ).group_by(Report.category).having(db.func.count(Report.category) > 20).all()
    user_data = []
    for user in users:
        count = Report.query.filter_by(username=user.username).count()
        accepted = Report.query.filter_by(username=user.username, approved='approved').count()
        level = (
            'خبير 🔥' if accepted >= 50 else
            'نشط 💪' if accepted >= 20 else
            'مشارك 🤝' if accepted >= 5 else
            'جديد 🐣'
        )
        user_data.append({
            'username': user.username,
            'phone': user.phone,
            'role': user.role,
            'reports': count,
            'approved': accepted,
            'level': level
        })
    return render_template('admin_dashboard.html', users=user_data, pending=pending, frequent=frequent)

# ✅ قبول بلاغ
@app.route('/accept/<int:id>')
def accept(id):
    r = Report.query.get(id)
    r.approved = 'approved'
    db.session.commit()
    return redirect('/admin_dashboard')

# ❌ رفض بلاغ
@app.route('/reject/<int:id>')
def reject(id):
    r = Report.query.get(id)
    r.approved = 'rejected'
    db.session.commit()
    return redirect('/admin_dashboard')

# 🗑️ حذف بلاغ
@app.route('/delete/<int:id>')
def delete(id):
    r = Report.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect('/admin_dashboard')

# 🚪 تسجيل خروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 🚀 بدء التشغيل
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
