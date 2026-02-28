import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='/home/ysnxng/Documents/projects/.env')

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def send_verification_email(to_email: str, code: str, expires_in_minutes: int = 5):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background:linear-gradient(135deg,#6366f1 0%,#1e1b4b 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="min-height:100vh;">
        <tr>
          <td align="center" valign="middle" style="padding:40px 20px;">
            <table width="400" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:24px;backdrop-filter:blur(10px);box-shadow:0 8px 40px rgba(0,0,0,0.3);">
              <tr>
                <td align="center" style="padding:48px 40px 32px;">

                  <!-- Icon -->
                  <div style="width:56px;height:56px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:16px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:28px;">
                    <span style="font-size:24px;"></span>
                  </div>

                  <!-- Title -->
                  <h1 style="margin:0 0 8px;color:white;font-size:1.6rem;font-weight:300;letter-spacing:-0.5px;opacity:0.95;">Verify your email</h1>
                  <p style="margin:0 0 36px;color:rgba(255,255,255,0.5);font-size:0.9rem;">Enter the code below to continue</p>

                  <!-- Code box -->
                  <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);border-radius:16px;padding:28px 40px;margin-bottom:28px;letter-spacing:12px;font-size:2.2rem;font-weight:600;color:white;text-align:center;">
                    {code}
                  </div>

                  <!-- Expiry note -->
                  <p style="margin:0 0 36px;color:rgba(255,255,255,0.4);font-size:0.8rem;">
                    ⏱ Expires in <strong style="color:rgba(255,255,255,0.6);">{expires_in_minutes} minutes</strong>
                  </p>

                  <!-- Divider -->
                  <div style="height:1px;background:rgba(255,255,255,0.1);margin-bottom:28px;"></div>

                  <!-- Footer -->
                  <p style="margin:0;color:rgba(255,255,255,0.3);font-size:0.75rem;line-height:1.6;">
                    If you didn't request this, you can safely ignore this email.<br>Do not share this code with anyone.
                  </p>

                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    response = requests.post(
        BREVO_URL,
        json={
            "sender": {"name": "Data science", "email": BREVO_SENDER_EMAIL},
            "to": [{"email": to_email, "name": to_email.split('@')[0]}],
            "subject": "Your verification code",
            "htmlContent": html
        },
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

    return response.json()

def send_password_reset_email(to_email: str, code: str, expires_in_minutes: int = 15):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background:linear-gradient(135deg,#6366f1 0%,#1e1b4b 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="min-height:100vh;">
        <tr>
          <td align="center" valign="middle" style="padding:40px 20px;">
            <table width="400" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:24px;backdrop-filter:blur(10px);box-shadow:0 8px 40px rgba(0,0,0,0.3);">
              <tr>
                <td align="center" style="padding:48px 40px 32px;">
                  <div style="width:56px;height:56px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:16px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:28px;">
                    <span style="font-size:24px;"></span>
                  </div>
                  <h1 style="margin:0 0 8px;color:white;font-size:1.6rem;font-weight:300;letter-spacing:-0.5px;opacity:0.95;">Reset your password</h1>
                  <p style="margin:0 0 36px;color:rgba(255,255,255,0.5);font-size:0.9rem;">Use the recovery code below to set a new password</p>
                  <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);border-radius:16px;padding:28px 40px;margin-bottom:28px;letter-spacing:12px;font-size:2.2rem;font-weight:600;color:white;text-align:center;">
                    {code}
                  </div>
                  <p style="margin:0 0 36px;color:rgba(255,255,255,0.4);font-size:0.8rem;">
                    ⏱ This link expires in <strong style="color:rgba(255,255,255,0.6);">{expires_in_minutes} minutes</strong>
                  </p>
                  <div style="height:1px;background:rgba(255,255,255,0.1);margin-bottom:28px;"></div>
                  <p style="margin:0;color:rgba(255,255,255,0.3);font-size:0.75rem;line-height:1.6;">
                    If you didn't request a password reset, you can safely ignore this email.<br>For security, never share this code with anyone.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    response = requests.post(
        BREVO_URL,
        json={
            "sender": {"name": "Data Science Workshop", "email": BREVO_SENDER_EMAIL},
            "to": [{"email": to_email, "name": to_email.split('@')[0]}],
            "subject": "Password Reset Request",
            "htmlContent": html
        },
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

    return response.json()