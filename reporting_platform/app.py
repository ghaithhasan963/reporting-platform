from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    password = db.Column(db.String(50))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    approved = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user'] = u
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm']:
            return 'كلمة المرور غير متطابقة'
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        report = Report(
            username=session['user'],
            category=request.form['category'],
            description=request.form['description']
        )
        db.session.add(report)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('submit_report.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    status = request.args.get('status')
    if status:
        reports = Report.query.filter_by(approved=status).all()
    else:
        reports = Report.query.all()
    return render_template('dashboard.html', reports=reports)

@app.route('/accept/<int:id>')
def accept(id):
    r = Report.query.get(id)
    r.approved = 'approved'
    db.session.commit()
    return redirect('/dashboard')

@app.route('/reject/<int:id>')
def reject(id):
    r = Report.query.get(id)
    r.approved = 'rejected'
    db.session.commit()
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    r = Report.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=10000, debug=True)
