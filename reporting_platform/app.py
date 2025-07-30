from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# 👤 نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    password = db.Column(db.String(50))
    role = db.Column(db.String(10), default='user')

# 📝 نموذج البلاغ
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    link = db.Column(db.String(250))
    report_type = db.Column(db.String(10), default='private')
    approved = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 🏠 الصفحة الترحيبية
@app.route('/')
def welcome():
    return render_template('welcome.html')

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

# 🆕 إنشاء حساب
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form.get('confirm'):
            return render_template('register.html', mismatch=True)
        new_user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            password=request.form['password'],
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# 📤 رفع بلاغ
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    if request.method == 'POST':
        last = Report.query.filter_by(username=session['user']).order_by(Report.created_at.desc()).first()
        if last and (datetime.utcnow() - last.created_at).seconds < 30:
            return render_template('submit_report.html', wait=True)
        report = Report(
            username=session['user'],
            category=request.form['category'],
            description=request.form['description'],
            link=request.form['link'],
            report_type=request.form['report_type']
        )
        db.session.add(report)
        db.session.commit()
        return render_template('submit_report.html', success=True)
    return render_template('submit_report.html')

# 🧍‍♂️ لوحة المستخدم
@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    reports = Report.query.filter_by(username=session['user']).all()
    approved = len([r for r in reports if r.approved == 'approved'])
    level = (
        'خبير 🔥' if approved >= 50 else
        'نشط 💪' if approved >= 20 else
        'مشارك 🤝' if approved >= 5 else
        'جديد 🐣'
    )
    return render_template('dashboard.html', reports=reports, level=level)

# 🛡️ لوحة الأدمن
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
    status = request.args.get('status')
    typ = request.args.get('type')
    q = Report.query
    if status: q = q.filter_by(approved=status)
    if typ: q = q.filter_by(report_type=typ)
    reports = q.order_by(Report.created_at.desc()).all()
    return render_template('admin_dashboard.html', reports=reports)

# ⚙️ إعدادات المستخدم
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' not in session:
        return redirect('/login')
    u = User.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        u.phone = request.form['phone']
        if request.form['password']:
            u.password = request.form['password']
        db.session.commit()
        return render_template('settings.html', updated=True)
    return render_template('settings.html')

# 👤 الملف الشخصي
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    u = User.query.filter_by(username=session['user']).first()
    reports = Report.query.filter_by(username=session['user']).all()
    approved = len([r for r in reports if r.approved == 'approved'])
    level = (
        'خبير 🔥' if approved >= 50 else
        'نشط 💪' if approved >= 20 else
        'مشارك 🤝' if approved >= 5 else
        'جديد 🐣'
    )
    return render_template('profile.html', user=u, reports=len(reports), level=level)

# 🗑️ إدارة البلاغات للأدمن
@app.route('/accept/<int:id>')
def accept(id):
    if session.get('role') != 'admin':
        return redirect('/login')
    r = Report.query.get(id)
    r.approved = 'approved'
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/reject/<int:id>')
def reject(id):
    if session.get('role') != 'admin':
        return redirect('/login')
    r = Report.query.get(id)
    r.approved = 'rejected'
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'admin':
        return redirect('/login')
    r = Report.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect('/admin_dashboard')

# 📄 صفحات ثابتة
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

# 🚪 تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 🚀 بدء السيرفر (متوافق مع Render)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
