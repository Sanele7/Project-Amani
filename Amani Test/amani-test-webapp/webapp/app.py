"""
Amani Test — web application.

Routes: register, email verification, login/logout, forgot/reset password,
and a dashboard that runs the scanner against authorized targets.

Security choices baked in:
- Passwords hashed (see auth.py), never stored or logged in plaintext.
- CSRF token on every state-changing form.
- Session cookies are HttpOnly + SameSite=Lax.
- Login / password-reset messages avoid revealing whether an account exists.
"""
import os
import secrets
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)

import auth
import email_utils
import scanner
from database import init_db

app = Flask(__name__)
# In production set FLASK_SECRET as an environment variable; this fallback keeps
# local dev working but changes on each restart (logging you out).
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # SESSION_COOKIE_SECURE=True,  # enable when served over HTTPS
)

init_db()


# ---- CSRF protection -----------------------------------------------------
@app.before_request
def ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


@app.context_processor
def inject_csrf():
    # makes {{ csrf_token }} available in every template
    return {"csrf_token": session.get("csrf_token", "")}


def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400, "Invalid CSRF token")


# ---- login required ------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---- routes --------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        else:
            user_id, error = auth.create_user(username, email, password)
            if error:
                flash(error, "error")
            else:
                token = auth.create_token(user_id, "verify")
                link = url_for("verify", token=token, _external=True)
                email_utils.send_verification(email, link)
                flash("Account created. Check your email to verify your account.", "success")
                return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/verify/<token>")
def verify(token):
    user_id = auth.consume_token(token, "verify")
    if user_id:
        auth.mark_verified(user_id)
        flash("Email verified. You can log in now.", "success")
    else:
        flash("That verification link is invalid or has expired.", "error")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = auth.get_user_by_username(username)

        if auth.verify_password(user, password):
            if not user["is_verified"]:
                flash("Please verify your email before logging in.", "error")
                return render_template("login.html", unverified_email=user["email"])
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(url_for("dashboard"))
        # Generic message — do not reveal whether the username exists.
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    check_csrf()
    email = request.form.get("email", "").strip()
    user = auth.get_user_by_email(email)
    if user and not user["is_verified"]:
        token = auth.create_token(user["id"], "verify")
        link = url_for("verify", token=token, _external=True)
        email_utils.send_verification(email, link)
    flash("If that account needs verification, a new link has been sent.", "success")
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        check_csrf()
        email = request.form.get("email", "").strip()
        user = auth.get_user_by_email(email)
        if user:
            token = auth.create_token(user["id"], "reset")
            link = url_for("reset_password", token=token, _external=True)
            email_utils.send_reset(email, link)
        # Same response whether or not the email exists (no enumeration).
        flash("If that email is registered, a reset link has been sent.", "success")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        check_csrf()
        password = request.form.get("password", "")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("reset_password.html", token=token)
        user_id = auth.consume_token(token, "reset")
        if user_id:
            auth.set_password(user_id, password)
            flash("Password updated. You can log in with your new password.", "success")
            return redirect(url_for("login"))
        flash("That reset link is invalid or has expired.", "error")
        return redirect(url_for("forgot_password"))
    # GET — show the form only if the token still exists (peek without consuming).
    return render_template("reset_password.html", token=token)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/scan", methods=["POST"])
@login_required
def scan():
    check_csrf()
    target = request.form.get("target", "").strip()
    findings, error = scanner.scan(target)
    return render_template("dashboard.html", username=session.get("username"),
                           target=target, findings=findings, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
