from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


# ---------- Register ----------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "")
        phone_number = request.form.get("phone_number", "").strip() or None

        

        if not name or len(name) < 2 or len(name) > 120:
            flash("Name is required (2-120 characters).", "error")
            return render_template("auth/register.html")

        if not email or "@" not in email:
            flash("Email is required.", "error")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        if role not in ("host", "customer"):
            flash("Invalid role selected.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "error")
            return render_template("auth/register.html")

        # --- Create user ---
        user = User(name=name, email=email, role=role, phone_number=phone_number)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ---------- Login ----------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("auth/login.html")


# ---------- Logout ----------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("property.index"))


# ---------- Dashboard Redirect ----------

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif current_user.role == "host":
        return redirect(url_for("host.dashboard"))
    elif current_user.role == "customer":
        return redirect(url_for("customer.dashboard"))
    logout_user()
    flash("Invalid user role.", "error")
    return redirect(url_for("auth.login"))
