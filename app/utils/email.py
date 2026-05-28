"""
Email utility for sending emails via Brevo (HTTP API or SMTP fallback)
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_otp_html(otp: str, email: str) -> str:
    """Build the OTP email HTML template matching the Figma design (node 114:5).

    Layout structure (600px card):
      1. Header bar (81px) – brand + nav
      2. Identity Alert – shield, label, heading, description
      3. OTP Module – grid bg, corner brackets, code box, timer
      4. Warning Callout – amber security notice
      5. Footer – nav links, copyright
    """
    # Spaced digits for the OTP (e.g. "8 3 4 9 7 6")
    otp_spaced = " ".join(otp)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<style>
  /* Subtle grid pattern background for the OTP module — email-safe fallback */
  .otp-grid-bg {{
    background-color: #F8FAFC;
    background-image:
      linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px);
    background-size: 20px 20px;
    background-position: center center;
  }}
  /* Outlook falls back to solid bg */
  .otp-digits {{
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Menlo, Consolas, monospace;
    font-size: 28px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: 6px;
  }}
</style>
</head>
<body style="margin:0;padding:0;background-color:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<!-- Outer wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F1F5F9;padding:48px 0;">
<tr><td align="center">

<!-- ===== CARD ===== -->
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF;border-radius:12px;overflow:hidden;">

<!-- ===== 1. HEADER (81px) ===== -->
<tr>
  <td style="background-color:#0F172A;padding:24px 24px;height:33px;">
    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="left" style="font-size:18px;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px;">Satrya Wiguna</td>
    </tr>
    </table>
  </td>
</tr>

<!-- ===== 2. IDENTITY ALERT ===== -->
<tr>
  <td style="padding:48px 24px 0 24px;">
    <!-- Shield icon + label row -->
    <table cellpadding="0" cellspacing="0">
    <tr>
      <td style="width:16px;vertical-align:middle;padding-right:8px;">
        <span style="font-size:14px;line-height:1;">&#128737;</span>
      </td>
      <td style="vertical-align:middle;font-size:12px;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:1px;">Identity Verification</td>
    </tr>
    </table>

    <!-- Heading -->
    <h1 style="margin:18px 0 0 0;font-size:28px;font-weight:700;color:#0F172A;line-height:1.2;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">Confirm Identity</h1>

    <!-- Description -->
    <p style="margin:16px 0 0 0;font-size:15px;color:#475569;line-height:1.6;">
      A sign&#8209;in attempt was detected for <strong style="color:#0F172A;">{email}</strong>.<br>
      To ensure the security of your account, please enter the verification code below.
    </p>
  </td>
</tr>

<!-- ===== 3. OTP MODULE ===== -->
<tr>
  <td style="padding:36px 24px 0 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" class="otp-grid-bg" style="border:1px solid #E2E8F0;border-radius:12px;">
      
      <!-- Top-left & top-right corner brackets -->
      <tr>
        <td style="padding:0;height:10px;">
          <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="width:10px;height:10px;border-top:2px solid #93C5FD;border-left:2px solid #93C5FD;border-radius:2px 0 0 0;"></td>
            <td></td>
            <td style="width:10px;height:10px;border-top:2px solid #93C5FD;border-right:2px solid #93C5FD;border-radius:0 2px 0 0;"></td>
          </tr>
          </table>
        </td>
      </tr>

      <!-- ENTER VERIFICATION CODE label -->
      <tr>
        <td style="padding:26px 24px 0 24px;text-align:center;">
          <span style="font-size:11px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:2px;">Enter Verification Code</span>
        </td>
      </tr>

      <!-- OTP code in bordered box -->
      <tr>
        <td style="padding:20px 0;text-align:center;">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto;background-color:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;">
          <tr>
            <td style="padding:12px 28px;">
              <span class="otp-digits">{otp_spaced}</span>
            </td>
          </tr>
          </table>
        </td>
      </tr>

      <!-- Timer -->
      <tr>
        <td style="padding:0 24px 26px 24px;text-align:center;">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
          <tr>
            <td style="vertical-align:middle;padding-right:6px;font-size:12px;line-height:1;">&#9201;</td>
            <td style="vertical-align:middle;font-size:12px;color:#94A3B8;">Code expires in <strong style="color:#64748B;font-weight:600;">10 minutes</strong></td>
          </tr>
          </table>
        </td>
      </tr>

      <!-- Bottom-left & bottom-right corner brackets -->
      <tr>
        <td style="padding:0;height:10px;">
          <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="width:10px;height:10px;border-bottom:2px solid #93C5FD;border-left:2px solid #93C5FD;border-radius:0 0 0 2px;"></td>
            <td></td>
            <td style="width:10px;height:10px;border-bottom:2px solid #93C5FD;border-right:2px solid #93C5FD;border-radius:0 0 2px 0;"></td>
          </tr>
          </table>
        </td>
      </tr>

    </table>
  </td>
</tr>

<!-- ===== 4. WARNING CALLOUT ===== -->
<tr>
  <td style="padding:32px 24px 48px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;">
    <tr>
      <td style="width:18px;padding:16px 0 16px 16px;vertical-align:top;">
        <span style="font-size:16px;line-height:1.3;">&#9888;</span>
      </td>
      <td style="padding:16px 16px 16px 12px;">
        <p style="margin:0;font-size:11px;font-weight:700;color:#C2410C;text-transform:uppercase;letter-spacing:0.8px;">Security Notice</p>
        <p style="margin:6px 0 0 0;font-size:13px;color:#9A3412;line-height:1.55;">
          If you did not initiate this sign&#8209;in attempt, please ignore this email. Your account security is important &mdash; never share this code with anyone.
        </p>
      </td>
    </tr>
    </table>
  </td>
</tr>

</table>
<!-- End Card -->

<!-- ===== 5. FOOTER ===== -->
<table width="600" cellpadding="0" cellspacing="0" style="margin-top:28px;">
<tr>
  <td style="text-align:center;padding:0 24px;">
    <p style="margin:0;font-size:12px;color:#94A3B8;">
      <span style="color:#64748B;">Satrya Wiguna</span>
      &nbsp;&middot;&nbsp;
      <span style="color:#64748B;">Portfolio</span>
      &nbsp;&middot;&nbsp;
      <span style="color:#64748B;">Privacy Policy</span>
    </p>
    <p style="margin:10px 0 6px 0;font-size:11px;color:#94A3B8;">
      &copy; 2026 Satrya Wiguna. All rights reserved.
    </p>
    <p style="margin:0;font-size:11px;color:#CBD5E1;">
      This is an automated security message &mdash; please do not reply.
    </p>
  </td>
</tr>
</table>

</td></tr>
</table>
</body>
</html>"""


async def send_otp_email(email: str, otp: str) -> bool:
    """
    Send OTP email.
    Uses Brevo HTTP API if BREVO_API_KEY is set (works even when SMTP ports are blocked).
    Falls back to SMTP otherwise.
    """
    if settings.BREVO_API_KEY:
        return await _send_via_brevo_api(email, otp)
    return await _send_via_smtp(email, otp)


async def _send_via_brevo_api(email: str, otp: str) -> bool:
    html_content = _build_otp_html(otp, email)
    payload = {
        "sender": {
            "name": settings.SMTP_FROM_NAME,
            "email": settings.SMTP_FROM_EMAIL,
        },
        "to": [{"email": email}],
        "subject": "Confirm Identity - Satrya Wiguna",
        "htmlContent": html_content,
        "textContent": (
            f"IDENTITY VERIFICATION\n"
            f"======================\n\n"
            f"A sign-in attempt was detected for {email}.\n"
            f"To ensure the security of your account, please use\n"
            f"the verification code below.\n\n"
            f"VERIFICATION CODE: {otp}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"⚠️  SECURITY NOTICE:\n"
            f"If you did not initiate this sign-in attempt, please\n"
            f"ignore this email. Never share this code with anyone.\n\n"
            f"--\n"
            f"Satrya Wiguna\n"
            f"This is an automated security message — please do not reply."
        ),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers={
                    "api-key": settings.BREVO_API_KEY,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
        logger.info(f"OTP email sent to {email} via Brevo API")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email} via Brevo API: {str(e)}")
        return False


async def _send_via_smtp(email: str, otp: str) -> bool:
    html_content = _build_otp_html(otp, email)
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = email
    message["Subject"] = "Confirm Identity - Satrya Wiguna"
    message.attach(MIMEText(
        f"IDENTITY VERIFICATION\n"
        f"======================\n\n"
        f"A sign-in attempt was detected for {email}.\n"
        f"To ensure the security of your account, please use\n"
        f"the verification code below.\n\n"
        f"VERIFICATION CODE: {otp}\n\n"
        f"This code expires in 10 minutes.\n\n"
        f"⚠️  SECURITY NOTICE:\n"
        f"If you did not initiate this sign-in attempt, please\n"
        f"ignore this email. Never share this code with anyone.\n\n"
        f"--\n"
        f"Satrya Wiguna\n"
        f"This is an automated security message — please do not reply.",
        "plain",
    ))
    message.attach(MIMEText(html_content, "html"))
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"OTP email sent to {email} via SMTP")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email} via SMTP: {str(e)}")
        return False
