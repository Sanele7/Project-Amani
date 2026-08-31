"""
Authentication logic for Amani Test.

The security decisions live here:
- Passwords are hashed with Werkzeug (scrypt by default), never stored in plaintext.
- Verification/reset tokens are high-entropy, single-use, and time-limited.
- Lookups use parameterised SQL to prevent injection.
- Login and password-reset responses are written to avoid *username enumeration*
  (the same weakness Amani Test flags in other apps).
"""
import secrets
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db

TOKEN_TTL_HOURS = {"verify": 24, "reset": 1}  # reset links expire fast


# ---- users ---------------------------------------------------------------
def create_user(username, email, password):
    """Create an unverified user. Returns (user_id, None) or (None, error)."""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email.lower(), generate_password_hash(password)),
        )
        conn.commit()
        return cur.lastrowid, None
    except Exception:
        # UNIQUE constraint — username or email already taken.
        return None, "That username or email is already registered."
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def get_user_by_email(email):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    conn.close()
    return row


def verify_password(user_row, password):
    return user_row and check_password_hash(user_row["password_hash"], password)


def mark_verified(user_id):
    conn = get_db()
    conn.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def set_password(user_id, new_password):
    conn = get_db()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(new_password), user_id),
    )
    conn.commit()
    conn.close()


# ---- tokens --------------------------------------------------------------
def create_token(user_id, purpose):
    """Issue a single-use, time-limited token for 'verify' or 'reset'."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS[purpose])
    conn = get_db()
    conn.execute(
        "INSERT INTO tokens (token, user_id, purpose, expires_at) VALUES (?, ?, ?, ?)",
        (token, user_id, purpose, expires.isoformat()),
    )
    conn.commit()
    conn.close()
    return token


def consume_token(token, purpose):
    """Validate and delete a token. Returns user_id, or None if invalid/expired."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tokens WHERE token = ? AND purpose = ?", (token, purpose)
    ).fetchone()
    if not row:
        conn.close()
        return None
    expired = datetime.fromisoformat(row["expires_at"]) < datetime.utcnow()
    # Single-use: remove it whether or not it was still valid.
    conn.execute("DELETE FROM tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return None if expired else row["user_id"]
