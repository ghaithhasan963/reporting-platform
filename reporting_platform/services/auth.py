from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('تم تسجيل الدخول بنجاح 👋', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح 🛑', 'info')
    return redirect(url_for('index'))
