from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from utils import calculate_trust_level

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    password = db.Column(db.String(50))
    role = db.Column(db.String(10), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    link = db.Column(db.String(200))  # 🔗 رابط منفصل
    report_type = db.Column(db.String(10), default='private')  # public/private
    approved = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return render_template('login.html', registered=True)
    return render_template('register.html')

@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    username = session['user']
    last_report = Report.query.filter_by(username=username).order_by(Report.created_at.desc()).first()
    wait = False
    if last_report:
        delta = datetime.utcnow() - last_report.created_at
        wait = delta < timedelta(seconds=30)
    if request.method == 'POST':
        if wait:
            return render_template('submit_report.html', wait=True)
        report = Report(
            username=username,
            category=request.form['category'],
            description=request.form['description'],
            link=request.form['link'],
            report_type=request.form['report_type']
        )
        db.session.add(report)
        db.session.commit()
        return render_template('submit_report.html', success=True)
    return render_template('submit_report.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'user':
        return redirect('/login')
    reports = Report.query.filter_by(username=session['user']).all()
    verified_reports = len([r for r in reports if r.approved == 'approved'])
    level = calculate_trust_level(verified_reports)
    return render_template('dashboard.html', reports=reports, level=level)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    user = User.query.filter_by(username=session['user']).first()
    reports = Report.query.filter_by(username=session['user']).all()
    verified_reports = len([r for r in reports if r.approved == 'approved'])
    level = calculate_trust_level(verified_reports)
    return render_template('profile.html', user=user, level=level, reports=len(reports))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
    status = request.args.get('status')
    report_type = request.args.get('type')
    query = Report.query
    if status:
        query = query.filter_by(approved=status)
    if report_type:
        query = query.filter_by(report_type=report_type)
    reports = query.order_by(Report.created_at.desc()).all()
    return render_template('admin_dashboard.html', reports=reports)

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

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000, debug=True)
