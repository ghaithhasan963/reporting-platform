from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# 🔐 جدول المستخدمين
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    password = db.Column(db.String(50))
    role = db.Column(db.String(10), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 📣 جدول البلاغات
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    link = db.Column(db.String(250))
    report_type = db.Column(db.String(10), default='private')  # عام/خاص
    approved = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def calculate_trust_level(count):
    if count >= 50: return 'خبير 🔥'
    elif count >= 20: return 'نشط 💪'
    elif count >= 5: return 'مشارك 🤝'
    else: return 'جديد 🐣'

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user'] = u
            session['role'] = user.role
            return redirect('/dashboard' if user.role == 'user' else '/admin_dashboard')
        return render_template('login.html', error=True)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm']:
            return render_template('register.html', mismatch=True)
        new_user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', registered=True)
    return render_template('register.html')

@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    last = Report.query.filter_by(username=session['user']).order_by(Report.created_at.desc()).first()
    wait = last and (datetime.utcnow() - last.created_at < timedelta(seconds=30))
    if request.method == 'POST':
        if wait: return render_template('submit_report.html', wait=True)
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

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'user': return redirect('/login')
    reports = Report.query.filter_by(username=session['user']).all()
    approved = len([r for r in reports if r.approved == 'approved'])
    level = calculate_trust_level(approved)
    return render_template('dashboard.html', reports=reports, level=level)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin': return redirect('/login')
    q = Report.query
    status = request.args.get('status')
    typ = request.args.get('type')
    if status: q = q.filter_by(approved=status)
    if typ: q = q.filter_by(report_type=typ)
    return render_template('admin_dashboard.html', reports=q.order_by(Report.created_at.desc()).all())

@app.route('/profile')
def profile():
    if 'user' not in session: return redirect('/login')
    u = User.query.filter_by(username=session['user']).first()
    reports = Report.query.filter_by(username=session['user']).all()
    approved = len([r for r in reports if r.approved == 'approved'])
    return render_template('profile.html', user=u, level=calculate_trust_level(approved), reports=len(reports))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' not in session: return redirect('/login')
    u = User.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        u.phone = request.form['phone']
        if request.form['password']:
            u.password = request.form['password']
        db.session.commit()
        return render_template('settings.html', updated=True)
    return render_template('settings.html')

@app.route('/accept/<int:id>')
def accept(id):
    if session.get('role') != 'admin': return redirect('/login')
    r = Report.query.get(id)
    r.approved = 'approved'
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/reject/<int:id>')
def reject(id):
    if session.get('role') != 'admin': return redirect('/login')
    r = Report.query.get(id)
    r.approved = 'rejected'
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'admin': return redirect('/login')
    r = Report.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000, debug=True)
