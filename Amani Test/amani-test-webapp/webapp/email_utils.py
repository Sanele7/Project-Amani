"""
Email delivery for verification and password-reset links.

Zero-budget friendly: if SMTP settings are provided via environment variables,
real email is sent. If not (e.g. local development), the link is printed to the
console instead so you can still complete the whole flow without an email account.

Free SMTP options when you're ready to send real mail:
- Gmail with an App Password (Google account > Security > App passwords)
- Brevo / Mailjet free tiers
Set: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
"""
import os
import smtplib
from email.message import EmailMessage


def _smtp_configured():
    return bool(os.environ.get("SMTP_HOST"))


def send_email(to_address, subject, body):
    if not _smtp_configured():
        # Development fallback — show the message (and its link) in the console.
        print("\n" + "=" * 60)
        print("[email not configured — showing message in console]")
        print(f"To:      {to_address}")
        print(f"Subject: {subject}")
        print("-" * 60)
        print(body)
        print("=" * 60 + "\n")
        return

    msg = EmailMessage()
    msg["From"] = os.environ.get("FROM_EMAIL", os.environ["SMTP_USER"])
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", 587))
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        server.send_message(msg)


def send_verification(to_address, link):
    send_email(
        to_address,
        "Verify your Amani Test account",
        f"Welcome to Amani Test.\n\nConfirm your email to activate your account:\n{link}\n\n"
        f"This link expires in 24 hours. If you didn't sign up, ignore this message.",
    )


def send_reset(to_address, link):
    send_email(
        to_address,
        "Reset your Amani Test password",
        f"We received a request to reset your password.\n\nSet a new password here:\n{link}\n\n"
        f"This link expires in 1 hour. If you didn't request this, ignore this message.",
    )
