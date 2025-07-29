from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
db = SQLAlchemy(app)

# 📦 تعريف نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    password = db.Column(db.String(50))

# 🛡️ تعريف نموذج البلاغ
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)

# 📥 تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user'] = u
            return redirect('/dashboard')
        return 'بيانات خاطئة'
    return render_template('login.html')

# 🧾 تسجيل مستخدم جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# 🚨 رفع بلاغ جديد
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if request.method == 'POST':
        report = Report(
            username=session.get('user'),
            category=request.form['category'],
            description=request.form['description']
        )
        db.session.add(report)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('submit_report.html')

# 📋 لوحة الإدارة
@app.route('/dashboard')
def dashboard():
    reports = Report.query.all()
    return render_template('dashboard.html', reports=reports)

# ✅ قبول بلاغ
@app.route('/accept/<int:id>')
def accept(id):
    r = Report.query.get(id)
    r.approved = True
    db.session.commit()
    return redirect('/dashboard')

# ❌ رفض بلاغ
@app.route('/reject/<int:id>')
def reject(id):
    r = Report.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect('/dashboard')

# 🔚 تشغيل السيرفر
if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=10000, debug=True)
