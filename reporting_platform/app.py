from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3, os, time, datetime
from werkzeug.utils import secure_filename
from utils import verify_screenshot, calculate_trust_level
from auth import hash_password, check_password
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
app = Flask(__name__)
app.secret_key = 'secret'
UPLOAD_FOLDER = 'screenshots/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🧑 تسجيل مستخدم
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = sqlite3.connect("platform.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit(); conn.close()
        return redirect('/login')
    return render_template('register.html')

# 🔑 تسجيل دخول
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pw_input = request.form['password']
        conn = sqlite3.connect("platform.db"); c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone(); conn.close()
        if user and check_password(user[1], pw_input):
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else: flash("❌ بيانات غير صحيحة")
    return render_template('login.html')

# 🏠 لوحة المستخدم
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/login')
    conn = sqlite3.connect("platform.db"); c = conn.cursor()
    c.execute("SELECT username, trust_level FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    c.execute("SELECT COUNT(*) FROM notifications WHERE recipient_id=?", (session['user_id'],))
    notif_count = c.fetchone()[0]
    conn.close()
    return render_template('dashboard.html', username=user[0], trust_level=user[1], notif_count=notif_count)

# 📬 إشعارات
@app.route('/notifications')
def notifications():
    if 'user_id' not in session: return redirect('/login')
    conn = sqlite3.connect("platform.db")
    c = conn.cursor()
    c.execute("SELECT message FROM notifications WHERE recipient_id=?", (session['user_id'],))
    notifs = c.fetchall()
    conn.close()
    return render_template('notifications.html', notifications=notifs)

# ⚠️ رفع بلاغ
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if 'user_id' not in session: return redirect('/login')
    if request.method == 'POST':
        url = request.form['url']
        desc = request.form['description']
        file = request.files['screenshot']
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        verified = verify_screenshot(path, url)
        conn = sqlite3.connect("platform.db"); c = conn.cursor()
        c.execute('''INSERT INTO reports (user_id, url, description, screenshot_path, created_at, is_verified)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], url, desc, path, datetime.datetime.now(), int(verified)))
        conn.commit()

        # تحديث مستوى الثقة
        c.execute("SELECT COUNT(*) FROM reports WHERE user_id=? AND is_verified=1", (session['user_id'],))
        count = c.fetchone()[0]
        level = calculate_trust_level(count)
        c.execute("UPDATE users SET trust_level=? WHERE id=?", (level, session['user_id']))
        conn.commit(); conn.close()
        flash("✅ تم رفع التقرير")
        return redirect('/dashboard')
    return render_template('submit_report.html')