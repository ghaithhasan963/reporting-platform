from flask import redirect, url_for, session, flash
from functools import wraps

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' not in session:
                flash('الرجاء تسجيل الدخول أولاً', 'error')
                return redirect(url_for('login'))
            if session['role'] != required_role:
                flash('ليس لديك صلاحية للدخول إلى هذا المسار', 'warning')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
