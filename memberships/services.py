from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import Membership, MembershipDecision


VALID_TRANSITIONS = {
    Membership.Status.DRAFT: {Membership.Status.SUBMITTED},
    Membership.Status.SUBMITTED: {
        Membership.Status.UNDER_REVIEW,
        Membership.Status.CORRECTIONS_REQUIRED,
        Membership.Status.APPROVED,
        Membership.Status.REFUSED,
    },
    Membership.Status.UNDER_REVIEW: {
        Membership.Status.CORRECTIONS_REQUIRED,
        Membership.Status.APPROVED,
        Membership.Status.REFUSED,
    },
    Membership.Status.CORRECTIONS_REQUIRED: {Membership.Status.SUBMITTED},
    Membership.Status.APPROVED: {Membership.Status.SUSPENDED},
    Membership.Status.SUSPENDED: {Membership.Status.APPROVED},
    Membership.Status.REFUSED: set(),
}

REASON_REQUIRED = {
    Membership.Status.CORRECTIONS_REQUIRED,
    Membership.Status.REFUSED,
    Membership.Status.SUSPENDED,
}


@transaction.atomic
def transition_membership(membership, actor, target_status, note=""):
    note = note.strip()
    allowed = VALID_TRANSITIONS.get(membership.status, set())
    if target_status not in allowed:
        raise ValidationError(
            _("A transição de %(from_status)s para %(to_status)s não é permitida."),
            params={
                "from_status": membership.get_status_display(),
                "to_status": Membership.Status(target_status).label,
            },
        )
    if target_status in REASON_REQUIRED and not note:
        raise ValidationError(_("Esta decisão exige uma justificação."))

    previous = membership.status
    membership.status = target_status
    update_fields = ["status", "updated_at"]

    if target_status == Membership.Status.SUBMITTED:
        membership.submitted_at = timezone.now()
        update_fields.append("submitted_at")
    if target_status in {Membership.Status.APPROVED, Membership.Status.REFUSED}:
        membership.decided_at = timezone.now()
        update_fields.append("decided_at")

    membership.save(update_fields=update_fields)
    return MembershipDecision.objects.create(
        membership=membership,
        actor=actor,
        from_status=previous,
        to_status=target_status,
        note=note,
    )
