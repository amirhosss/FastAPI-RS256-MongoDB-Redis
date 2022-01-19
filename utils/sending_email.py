import logging
from typing import Any
from pathlib import Path

import emails
from emails.template import JinjaTemplate

from core.config import settings


def send_email(
    email_to: str,
    subject_template: str,
    html_template: str,
    environment: dict[str, Any]
):
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAIL_FROM_NAME, settings.EMAIL_FROM)
    )
    smtp_options = {
        'host': settings.SMTP_SERVER,
        'port': settings.SMTP_SERVER_PORT,
        'ssl': True,
        'user': settings.EMAIL_FROM,
        'password': settings.EMAIL_FROM_PASSWORD
    }
    
    response = message.send(render=environment, to=email_to, smtp=smtp_options)
    logging.info(f'send email response: {response}')


def send_verification_email(name: str, email_to: str , token: str):
    subject = 'Email verification'
    with open(Path(settings.EMAIL_TEMPLATE_DIR)/'email_verification.jinja2') as f:
        template = f.read()
    link = f'{settings.SERVER_HOST}/api/auth/verification?token={token}'
    env = {
        'name': name,
        'verification_link': link
    }
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template,
        environment=env
    )


def send_reset_password_email(name: str, email_to: str, public_id: str, token: str):
    subject = 'Reset password'
    with open(Path(settings.EMAIL_TEMPLATE_DIR)/'reset_password.jinja2') as f:
        template = f.read()
    link = f'{settings.SERVER_HOST}/api/user/{public_id}/reset-password?token={token}'
    env = {
        'name': name,
        'verification_link': link
    }
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template,
        environment=env
    )