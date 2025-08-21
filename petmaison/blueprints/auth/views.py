from __future__ import annotations

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from ...extensions import db
from ...models import User

bp = Blueprint("auth", __name__, template_folder="../../templates")


def role_required(*roles: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("No tienes permisos", "danger")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)

        return wrapper

    return decorator


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard.index"))
        flash("Credenciales inválidas", "danger")
    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
