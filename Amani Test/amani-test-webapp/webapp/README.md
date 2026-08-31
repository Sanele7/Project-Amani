# Amani Test — Web Application

A branded web front-end for the Amani Test scanner, with real user accounts:
registration, email verification, login, forgot/reset password, and a dashboard
that runs the scanner against authorized targets.

Built with Flask + SQLite. No paid services required.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 — you'll land on the login screen. Create an account;
the verification link is printed to the console (see "Email" below), so you can
complete the whole flow locally without an email provider.

## How the security is built

This is a security tool, so the login is built to the standard the tool itself
checks for:

- **Passwords are hashed** with scrypt (via Werkzeug) — never stored in plaintext.
- **Verification and reset tokens** are high-entropy, single-use, and time-limited
  (verify: 24h, reset: 1h).
- **All SQL is parameterised** — no string-built queries, so no SQL injection in
  the app's own code.
- **CSRF tokens** guard every state-changing form.
- **Login and password-reset messages are generic** — they don't reveal whether a
  username or email exists (avoids user enumeration).
- **Session cookies** are HttpOnly + SameSite=Lax.

## Email

By default (no SMTP configured) verification/reset links are printed to the
console — ideal for local development.

To send real email, set these environment variables (free options: a Gmail
App Password, or Brevo/Mailjet free tiers):

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=you@gmail.com
export SMTP_PASS=your_app_password
export FROM_EMAIL=you@gmail.com
```

## Branding

The neon "Secured by Impunga Yehlathi" wordmark is rendered in CSS
(`static/style.css`) so it stays crisp at any size and sits small at the bottom
of every page, as specified. To use your own PNG instead, drop it in `static/`
and swap the `.brandmark` block in `templates/base.html` for an `<img>`.

## Before deploying publicly (production checklist)

- Set a fixed `FLASK_SECRET` environment variable (currently random per restart).
- Serve over HTTPS and enable `SESSION_COOKIE_SECURE=True` in `app.py`.
- Add **rate limiting** on login, registration, and forgot-password
  (e.g. Flask-Limiter) to resist brute force.
- Run behind a production server (gunicorn/uwsgi), not the Flask dev server.
- Consider hashing tokens at rest for extra hardening.

## Files

- `app.py` — routes and request handling
- `auth.py` — user + token logic, password hashing
- `database.py` — SQLite schema and connection
- `email_utils.py` — email delivery (SMTP or console)
- `scanner.py` — the dashboard's scan (scope check + header/XSS checks)
- `authorized_targets.txt` — the scope whitelist the scanner enforces
- `templates/`, `static/` — the neon interface
