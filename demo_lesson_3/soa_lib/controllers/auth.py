from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import User

auth_bp = Blueprint("auth", __name__)

def is_logged_in():
    return bool(session.get("user_id"))

def login_required(view_fn):
    from functools import wraps
    @wraps(view_fn)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("auth.login"))
        return view_fn(*args, **kwargs)
    return wrapper

@auth_bp.get("/login")
def login():
    if is_logged_in():
        return redirect(url_for("admin.dashboard"))
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        flash("Sai thông tin đăng nhập", "error")
        return redirect(url_for("auth.login"))
    session["user_id"] = user.id
    session["full_name"] = user.full_name
    return redirect(url_for("admin.dashboard"))

@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))