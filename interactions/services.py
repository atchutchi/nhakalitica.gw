import csv
from io import StringIO
from collections.abc import Mapping
from datetime import timedelta
from hashlib import sha256

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Case, IntegerField, Prefetch, When
from django.urls import reverse
from django.utils import timezone

from memberships.models import Membership
from profiles.models import Profile

from .models import ContactRequest, Favorite, Notification, ProfileLike, RecruitmentTag, Report, SavedSearch


SHORTLIST_CSV_HEADERS = [
    "Nome publico",
    "Titulo profissional",
    "Sector",
    "Area",
    "Pais publico",
    "Modalidade",
    "Disponibilidade",
    "Competencias",
    "Idiomas",
    "Estado",
    "Etiquetas",
    "Notas",
    "URL do perfil",
]


def clean_saved_search_params(params: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value.strip()
        for key, value in params.items()
        if key in SavedSearch.allowed_query_params() and isinstance(value, str) and value.strip()
    }


@transaction.atomic
def sync_favorite_tags(favorite: Favorite, raw_tags: str) -> list[RecruitmentTag]:
    tags = []
    seen_names = set()
    for raw_name in raw_tags.split(","):
        name = " ".join(raw_name.split())
        normalized_name = RecruitmentTag.objects.normalise_name(name)
        if not name or normalized_name in seen_names:
            continue
        tag, _created = RecruitmentTag.objects.get_or_create(
            user=favorite.user,
            normalized_name=normalized_name,
            defaults={"name": name},
        )
        tags.append(tag)
        seen_names.add(normalized_name)
    favorite.tags.set(tags)
    return tags


def get_comparable_favorites(user, profile_ids: list[int]):
    membership = getattr(user, "membership", None)
    if not membership or not membership.can_access_network:
        return Favorite.objects.none()
    unique_ids = []
    for profile_id in profile_ids:
        if isinstance(profile_id, bool):
            continue
        try:
            numeric_id = int(profile_id)
        except (TypeError, ValueError):
            continue
        if numeric_id > 0 and numeric_id not in unique_ids:
            unique_ids.append(numeric_id)
        if len(unique_ids) == 4:
            break
    ordering = Case(
        *[When(profile_id=profile_id, then=position) for position, profile_id in enumerate(unique_ids)],
        output_field=IntegerField(),
    )
    return (
        Favorite.objects.filter(
            user=user,
            profile_id__in=unique_ids,
            profile__review_status=Profile.ReviewStatus.APPROVED,
            profile__is_discoverable=True,
            profile__user__membership__status=Membership.Status.APPROVED,
        )
        .select_related("profile")
        .order_by(ordering)
    )


def _csv_safe(value) -> str:
    value = str(value or "")
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


def build_shortlist_csv(user, favorites) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=SHORTLIST_CSV_HEADERS)
    writer.writeheader()
    membership = getattr(user, "membership", None)
    if not membership or not membership.can_access_network:
        return f"\ufeff{output.getvalue()}"
    for favorite in favorites.filter(
        user=user,
        profile__review_status=Profile.ReviewStatus.APPROVED,
        profile__is_discoverable=True,
        profile__user__membership__status=Membership.Status.APPROVED,
    ).select_related("profile").prefetch_related(
        Prefetch("tags", queryset=RecruitmentTag.objects.filter(user=user), to_attr="owned_tags")
    ):
        profile = favorite.profile
        payload = profile.public_payload
        writer.writerow(
            {
                "Nome publico": _csv_safe(profile.public_display_name),
                "Titulo profissional": _csv_safe(profile.public_professional_title),
                "Sector": _csv_safe(", ".join(payload.get("sectors", []))),
                "Area": _csv_safe(", ".join(payload.get("areas", []))),
                "Pais publico": _csv_safe(profile.public_country),
                "Modalidade": _csv_safe(
                    payload.get("work_preference_label", "")
                    if profile.published_snapshot
                    else profile.get_work_preference_display()
                ),
                "Disponibilidade": _csv_safe(
                    payload.get("availability_label", "")
                    if profile.published_snapshot
                    else profile.get_availability_display()
                ),
                "Competencias": _csv_safe(", ".join(profile.public_skill_names)),
                "Idiomas": _csv_safe(", ".join(language.get("name", "") for language in payload.get("languages", []))),
                "Estado": _csv_safe(favorite.get_status_display()),
                "Etiquetas": _csv_safe(", ".join(tag.name for tag in favorite.owned_tags)),
                "Notas": _csv_safe(favorite.notes),
                "URL do perfil": _csv_safe(reverse("public-profile", args=(profile.slug,))),
            }
        )
    return f"\ufeff{output.getvalue()}"


def ensure_member_profile_action(user, profile):
    if profile.user_id == user.id:
        raise PermissionDenied("Não podes executar esta ação no teu próprio perfil.")
    if not profile.is_visible_to(user):
        raise PermissionDenied("Este perfil não está disponível.")


def toggle_relation(model, user, profile):
    ensure_member_profile_action(user, profile)
    relation, created = model.objects.get_or_create(user=user, profile=profile)
    if not created:
        relation.delete()
    return created


def toggle_favorite(user, profile):
    return toggle_relation(Favorite, user, profile)


def add_favorite(user, profile):
    ensure_member_profile_action(user, profile)
    return Favorite.objects.get_or_create(user=user, profile=profile)


def toggle_like(user, profile):
    return toggle_relation(ProfileLike, user, profile)


@transaction.atomic
def create_contact(sender, profile, subject, message, remote_address=""):
    ensure_member_profile_action(sender, profile)
    if not sender.email_verified_at:
        raise ValidationError("Confirma o teu email antes de enviares contactos.")
    if not profile.consent_contact or profile.contact_visibility == Profile.ContactVisibility.HIDDEN:
        raise ValidationError("Este profissional não está a aceitar contactos.")
    since = timezone.now() - timedelta(hours=1)
    recent_count = ContactRequest.objects.filter(
        sender=sender, profile=profile, created_at__gte=since
    ).count()
    if recent_count >= 3:
        raise ValidationError("Atingiste o limite de mensagens para este perfil. Tenta novamente mais tarde.")
    ip_hash = sha256(f"{settings.SECRET_KEY}:{remote_address}".encode()).hexdigest() if remote_address else ""
    contact = ContactRequest.objects.create(
        sender=sender,
        profile=profile,
        subject=subject,
        message=message,
        sender_ip_hash=ip_hash,
    )
    Notification.objects.create(
        user=profile.user,
        type="new_contact",
        title="Novo pedido de contacto",
        body=f"Recebeste uma mensagem sobre: {subject}",
        link=reverse("interactions:contacts"),
    )
    send_mail(
        subject=f"Kalitica: {subject}",
        message="Recebeste um novo pedido de contacto. Inicia sessão na Kalitica para consultar a mensagem.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[profile.user.email],
        fail_silently=True,
    )
    return contact


@transaction.atomic
def create_report(reporter, profile, reason, description=""):
    ensure_member_profile_action(reporter, profile)
    if Report.objects.filter(
        reporter=reporter,
        profile=profile,
        status__in=(Report.Status.OPEN, Report.Status.REVIEWING),
    ).exists():
        raise ValidationError("Já existe uma denúncia activa para este perfil.")
    report = Report.objects.create(
        reporter=reporter, profile=profile, reason=reason, description=description
    )
    staff_ids = profile.user.__class__.objects.filter(is_staff=True, is_active=True).values_list("id", flat=True)
    Notification.objects.bulk_create(
        [
            Notification(
                user_id=user_id,
                type="new_report",
                title="Nova denúncia de perfil",
                body=f"Foi criada uma denúncia para {profile}.",
                link=reverse("moderation:report-list"),
            )
            for user_id in staff_ids
        ]
    )
    return report
