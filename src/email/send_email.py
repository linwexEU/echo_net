import smtplib 
from src.config import settings
from pydantic import EmailStr
from src.email.email_templates import create_reset_password_confirmation_template


def send_email_about_password_reset(to_: EmailStr, from_: EmailStr, pin_code: int, ip: str, device: str, browser: str): 
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server: 
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(create_reset_password_confirmation_template(to_, from_, pin_code, ip, device, browser))
