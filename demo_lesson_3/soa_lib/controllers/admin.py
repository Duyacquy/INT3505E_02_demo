from flask import Blueprint, render_template, session, redirect, url_for
from .auth import login_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/")
def root():
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("auth.login"))

@admin_bp.get("/admin")
@login_required
def dashboard():
    full_name = session.get("full_name", "Admin")
    return render_template("admin.html", full_name=full_name)
