from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    url = request.build_absolute_uri(reverse("accounts:verify-email", args=(uid, token)))
    send_mail(
        subject="Confirma o teu email na Kalitica",
        message=f"Confirma o teu endereço de email através desta ligação temporária:\n\n{url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
