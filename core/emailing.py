import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def send_template_email(template_prefix, recipient_list, context):
    recipients = [item for item in recipient_list if item]
    if not recipients:
        return
    subject = render_to_string(
        f"emails/{template_prefix}_subject.txt",
        context,
    ).strip()
    body = render_to_string(
        f"emails/{template_prefix}_body.txt",
        context,
    )
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Falha ao enviar email operacional",
            extra={"template": template_prefix},
        )
