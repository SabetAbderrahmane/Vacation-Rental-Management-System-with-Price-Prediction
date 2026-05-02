"""
Role protection decorators — Task 3.3

Usage in route files:
    from routes.utils import admin_required, host_required, customer_required

    @host_bp.route("/dashboard")
    @login_required
    @host_required
    def dashboard():
        ...
"""

from functools import wraps
from flask import flash, redirect, url_for, render_template
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("You do not have permission to access this page.", "error")
            return render_template("errors/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def host_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "host":
            flash("You do not have permission to access this page.", "error")
            return render_template("errors/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "customer":
            flash("You do not have permission to access this page.", "error")
            return render_template("errors/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function
