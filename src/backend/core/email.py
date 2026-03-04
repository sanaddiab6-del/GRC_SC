"""
Email utility for SICO GRC Platform.
Sends plain-text / HTML emails via SMTP.

Configuration:
    Set EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS in your .env file.
    If EMAIL_HOST is empty the helper logs a warning and skips sending —
    the application will continue without crashing.
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    *,
    to_address: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> bool:
    """
    Send an email.

    Returns True on success, False if SMTP is not configured or sending fails.
    Never raises — all exceptions are caught and logged.
    """
    if not settings.EMAIL_HOST or not settings.EMAIL_USER:
        logger.warning(
            "Email not sent to %s — SMTP is not configured "
            "(set EMAIL_HOST / EMAIL_USER / EMAIL_PASS in your .env).",
            to_address,
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_USER}>"
        msg["To"] = to_address

        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.sendmail(settings.EMAIL_USER, to_address, msg.as_string())

        logger.info("Email sent to %s — subject: %s", to_address, subject)
        return True

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send email to %s: %s", to_address, exc)
        return False


# ── Template helpers ──────────────────────────────────────────────────────────

def send_account_approved_email(
    *,
    to_address: str,
    full_name: str,
    login_url: str = "http://localhost:3000/en/login",
) -> bool:
    """Send account-approved notification email (bilingual)."""
    subject = "Your SICO GRC account has been approved / تمت الموافقة على حسابك"

    body_text = (
        f"Dear {full_name},\n\n"
        "Your account on the SICO GRC platform has been approved by the administrator.\n"
        f"You can now log in at: {login_url}\n\n"
        "---\n"
        f"عزيزي {full_name}،\n\n"
        "تمت الموافقة على حسابك في منصة SICO GRC من قِبل المسؤول.\n"
        f"يمكنك الآن تسجيل الدخول على: {login_url}\n\n"
        "SICO GRC Platform"
    )

    body_html = f"""
<!DOCTYPE html>
<html dir="ltr" lang="en">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="color:#1d4ed8;font-size:28px;margin:0;">SICO GRC</h1>
    <p style="color:#64748b;margin:4px 0;">Governance, Risk &amp; Compliance Platform</p>
  </div>
  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:24px;margin-bottom:24px;">
    <h2 style="color:#15803d;margin-top:0;">&#10003; Account Approved</h2>
    <p>Dear <strong>{full_name}</strong>,</p>
    <p>Your account on the SICO GRC platform has been <strong>approved</strong> by an administrator.</p>
    <a href="{login_url}"
       style="display:inline-block;background:#1d4ed8;color:white;padding:12px 24px;
              border-radius:8px;text-decoration:none;font-weight:bold;margin-top:12px;">
      Log In Now
    </a>
  </div>
  <div style="background:#fefce8;border:1px solid #fde68a;border-radius:12px;padding:24px;direction:rtl;text-align:right;">
    <h2 style="color:#92400e;margin-top:0;">✓ تمت الموافقة على الحساب</h2>
    <p>عزيزي <strong>{full_name}</strong>،</p>
    <p>تمت الموافقة على حسابك في منصة SICO GRC من قِبل المسؤول.</p>
    <a href="{login_url}"
       style="display:inline-block;background:#1d4ed8;color:white;padding:12px 24px;
              border-radius:8px;text-decoration:none;font-weight:bold;margin-top:12px;">
      تسجيل الدخول الآن
    </a>
  </div>
  <p style="color:#94a3b8;font-size:12px;text-align:center;margin-top:24px;">
    SICO GRC Platform — Automated notification, do not reply.
  </p>
</body>
</html>
"""
    return send_email(
        to_address=to_address,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
    )


def send_account_denied_email(
    *,
    to_address: str,
    full_name: str,
) -> bool:
    """Send account-denied notification email (bilingual)."""
    subject = "Update on your SICO GRC access request / تحديث حول طلب الوصول"

    body_text = (
        f"Dear {full_name},\n\n"
        "We regret to inform you that your access request to the SICO GRC platform "
        "has not been approved at this time.\n"
        "Please contact your administrator for more information.\n\n"
        "---\n"
        f"عزيزي {full_name}،\n\n"
        "نأسف لإبلاغكم بأن طلب الوصول إلى منصة SICO GRC لم تتم الموافقة عليه في الوقت الحالي.\n"
        "يرجى التواصل مع المسؤول للمزيد من المعلومات.\n\n"
        "SICO GRC Platform"
    )

    return send_email(
        to_address=to_address,
        subject=subject,
        body_text=body_text,
    )
