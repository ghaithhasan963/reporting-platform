from flask import Flask, render_template, redirect, url_for, request, session, flash
from auth import hash_password, verify_password
from db_init import init_db, add_user, find_user, save_report, get_reports
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # لتخزين الجلسات

init_db()

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = hash_password(request.form.get("password"))
        add_user(username, password)
        flash("✅ تم التسجيل بنجاح!")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username)
        if user and verify_password(password, user["password"]):
            session["user"] = username
            flash("✅ تم تسجيل الدخول!")
            return redirect(url_for("dashboard"))
        flash("❌ معلومات خاطئة")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    reports = get_reports()
    return render_template("dashboard.html", reports=reports, user=user)

@app.route("/submit", methods=["GET", "POST"])
def submit_report():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        content = request.form.get("report")
        save_report(content, session["user"])
        flash("✅ تم إرسال البلاغ")
        return redirect(url_for("dashboard"))
    return render_template("submit_report.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("🚪 تم تسجيل الخروج")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)

