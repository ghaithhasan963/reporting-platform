from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# 👤 نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

# 📝 نموذج البلاغ
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# 📅 تمرير السنة إلى القوالب
@app.context_processor
def inject_year():
    return {"current_year": datetime.datetime.now().year}

# 🏠 الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("welcome.html")

# 🔐 تسجيل الحساب
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not confirm or password != confirm:
            return "كلمة المرور وتأكيدها غير متطابقين", 400

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("register.html")

# 🔓 تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        return "بيانات الدخول غير صحيحة", 401
    return render_template("login.html")

# 🚪 تسجيل الخروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# 🧭 لوحة التحكم
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# 📤 رفع بلاغ
@app.route("/submit_report", methods=["GET", "POST"])
def submit_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        content = request.form.get("content")
        report = Report(content=content, user_id=session["user_id"])
        db.session.add(report)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("submit_report.html")

# ℹ️ صفحة "من نحن"
@app.route("/about")
def about():
    return render_template("about.html")

# ⚖️ صفحة "سياسة الاستخدام"
@app.route("/policy")
def policy():
    return render_template("policy.html")

# 🚀 تشغيل السيرفر
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
