from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from profiles.models import Profile, ProfileRevision

from .models import AuditLog


ACTION_CONFIG = {
    "approve": {
        "status": Profile.Status.APPROVED,
        "audit_action": "profile.approved",
        "requires_reason": False,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "reject": {
        "status": Profile.Status.REJECTED,
        "audit_action": "profile.rejected",
        "requires_reason": True,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "request_changes": {
        "status": Profile.Status.DRAFT,
        "audit_action": "profile.changes_requested",
        "requires_reason": True,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "suspend": {
        "status": Profile.Status.SUSPENDED,
        "audit_action": "profile.suspended",
        "requires_reason": True,
        "allowed": {
            Profile.Status.PENDING,
            Profile.Status.APPROVED,
            Profile.Status.REJECTED,
            Profile.Status.CHANGES_PENDING,
        },
    },
    "restore": {
        "status": Profile.Status.DRAFT,
        "audit_action": "profile.restored",
        "requires_reason": True,
        "allowed": {Profile.Status.SUSPENDED},
    },
}


@transaction.atomic
def moderate_profile(profile, actor, action, reason=""):
    try:
        config = ACTION_CONFIG[action]
    except KeyError as error:
        raise ValidationError("Ação de moderação inválida.") from error

    locked_profile = Profile.objects.select_for_update().select_related("user").get(pk=profile.pk)
    clean_reason = reason.strip()
    if locked_profile.status not in config["allowed"]:
        raise ValidationError("Esta ação não é válida para o estado atual do perfil.")
    if config["requires_reason"] and not clean_reason:
        raise ValidationError("Indica o motivo da decisão.")

    previous_status = locked_profile.status
    now = timezone.now()
    keeps_previous_public_version = previous_status == Profile.Status.CHANGES_PENDING and action in {
        "reject",
        "request_changes",
    }
    locked_profile.status = Profile.Status.APPROVED if keeps_previous_public_version else config["status"]
    locked_profile.is_public = action == "approve" or keeps_previous_public_version
    locked_profile.review_note = clean_reason
    locked_profile.reviewed_by = actor
    locked_profile.reviewed_at = now
    if action == "approve":
        locked_profile.approved_at = now
        locked_profile.published_snapshot = locked_profile.build_public_snapshot()
        locked_profile.published_at = now
    elif action in {"reject", "request_changes", "suspend", "restore"} and not keeps_previous_public_version:
        locked_profile.approved_at = None
    locked_profile.save(
        update_fields=(
            "status",
            "is_public",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "approved_at",
            "published_snapshot",
            "published_at",
            "updated_at",
        )
    )

    if action == "suspend":
        locked_profile.user.is_active = False
        locked_profile.user.save(update_fields=("is_active",))
    elif action == "restore":
        locked_profile.user.is_active = True
        locked_profile.user.save(update_fields=("is_active",))

    AuditLog.objects.create(
        actor=actor,
        action=config["audit_action"],
        target_type="profile",
        target_id=str(locked_profile.pk),
        metadata={"previous_status": previous_status, "new_status": locked_profile.status},
    )
    revision = locked_profile.revisions.filter(status=ProfileRevision.Status.PENDING).first()
    revision_status = {
        "approve": ProfileRevision.Status.APPROVED,
        "reject": ProfileRevision.Status.REJECTED,
        "request_changes": ProfileRevision.Status.REJECTED,
    }.get(action)
    if revision_status:
        if revision is None:
            revision = ProfileRevision(
                profile=locked_profile,
                submitted_by=locked_profile.user,
                payload=locked_profile.build_public_snapshot(),
            )
        revision.status = revision_status
        revision.review_note = clean_reason
        revision.reviewed_by = actor
        revision.reviewed_at = now
        revision.save()
    from interactions.models import Notification

    notification_titles = {
        "approve": "Perfil aprovado",
        "reject": "Perfil rejeitado",
        "request_changes": "Correcções solicitadas",
        "suspend": "Conta suspensa",
        "restore": "Conta restaurada",
    }
    Notification.objects.create(
        user=locked_profile.user,
        type=f"profile_{action}",
        title=notification_titles[action],
        body=clean_reason,
        link="/conta/painel/",
    )
    return locked_profile


@transaction.atomic
def moderate_report(report, actor, action, note=""):
    from interactions.models import Notification, Report

    statuses = {
        "review": (Report.Status.REVIEWING, "report.reviewing"),
        "resolve": (Report.Status.RESOLVED, "report.resolved"),
        "dismiss": (Report.Status.DISMISSED, "report.dismissed"),
    }
    try:
        new_status, audit_action = statuses[action]
    except KeyError as error:
        raise ValidationError("Ação de denúncia inválida.") from error
    clean_note = note.strip()
    if action in {"resolve", "dismiss"} and not clean_note:
        raise ValidationError("Indica a resolução da denúncia.")

    locked_report = Report.objects.select_for_update().get(pk=report.pk)
    locked_report.status = new_status
    locked_report.assigned_to = actor
    locked_report.resolution_note = clean_note
    locked_report.resolved_at = timezone.now() if action in {"resolve", "dismiss"} else None
    locked_report.save(
        update_fields=("status", "assigned_to", "resolution_note", "resolved_at")
    )
    AuditLog.objects.create(
        actor=actor,
        action=audit_action,
        target_type="report",
        target_id=str(locked_report.pk),
        metadata={"new_status": new_status, "profile_id": locked_report.profile_id},
    )
    if action in {"resolve", "dismiss"}:
        Notification.objects.create(
            user=locked_report.reporter,
            type="report_resolved",
            title="Denúncia analisada",
            body="A equipa concluiu a análise da tua denúncia.",
            link="",
        )
    return locked_report
