from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///savenet.db'
db = SQLAlchemy(app)

# --- نماذج البيانات ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), default='زائر')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))

last_report_time = time.time()

# صفحة الهبوط العامة
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    user_count = User.query.count()
    reports = Report.query.all()
    return render_template('home.html', user_count=user_count, reports=reports)

# الصفحة الرئيسية للمستخدم بعد تسجيل الدخول
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    user = User.query.get(session['user_id'])
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template("dashboard.html", reports=reports, user=user)

# صفحة إرسال بلاغ جديد
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        report = Report(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            date=datetime.today().strftime('%Y-%m-%d')
        )
        db.session.add(report)
        db.session.commit()
        global last_report_time
        last_report_time = time.time()
        return redirect('/dashboard')
    return render_template('report.html')

# تسجيل مستخدم جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        user = User(
            username=request.form['username'],
            password=hashed_pw,
            phone=request.form['phone'],
            role='زائر'
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/dashboard')
        return render_template('login.html', error='بيانات الدخول غير صحيحة')
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# لوحة تحكم المشرف
@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'مشرف':
        return redirect('/')
    users = User.query.all()
    reports = Report.query.order_by(Report.id.desc()).all()
    user_count = User.query.count()
    return render_template("admin.html", users=users, reports=reports, user_count=user_count)

@app.route('/admin/update_role', methods=['POST'])
def update_role():
    if 'user_id' not in session or session.get('role') != 'مشرف':
        return redirect('/')
    user = User.query.get(int(request.form['user_id']))
    if user:
        user.role = request.form['role']
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'user_id' not in session or session.get('role') != 'مشرف':
        return redirect('/')
    user = User.query.get(int(request.form['user_id']))
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/check_new_reports')
def check_new_reports():
    is_new = (time.time() - last_report_time) < 35
    return jsonify({"new_reports": is_new})

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
