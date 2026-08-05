from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.emailing import send_template_email

from .tokens import email_verification_token


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    url = request.build_absolute_uri(reverse("accounts:verify-email", args=(uid, token)))
    send_template_email(
        "verification",
        [user.email],
        {"user": user, "verification_url": url},
    )
