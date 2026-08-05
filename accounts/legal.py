from django.conf import settings

from .models import LegalAcceptance


def record_legal_acceptance(user, document_type, source):
    acceptance, _created = LegalAcceptance.objects.get_or_create(
        user=user,
        document_type=document_type,
        version=settings.LEGAL_DOCUMENT_VERSION,
        source=source,
    )
    return acceptance
