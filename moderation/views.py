from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from memberships.models import Membership
from memberships.services import VALID_TRANSITIONS
from profiles.models import Profile

from .models import AuditLog
from .services import (
    ACTION_CONFIG,
    MEMBERSHIP_MODERATION_TARGETS,
    moderate_membership,
    moderate_profile,
    moderate_report,
)


PROFILE_ACTION_LABELS = {
    "approve": _("Aprovar publicação"),
    "request_changes": _("Pedir correcções"),
    "reject": _("Recusar"),
    "suspend": _("Suspender"),
    "restore": _("Restaurar"),
}


def available_profile_actions(status):
    return [
        {
            "value": action,
            "label": PROFILE_ACTION_LABELS[action],
            "css_class": {
                "approve": "admin-action-approved",
                "request_changes": "admin-action-corrections_required",
                "reject": "admin-action-refused",
                "suspend": "admin-action-suspended",
            }.get(action, ""),
            "confirmation": {
                "reject": _("Confirmas a recusa deste perfil?"),
                "suspend": _("Confirmas a suspensão deste perfil?"),
            }.get(action, ""),
        }
        for action, config in ACTION_CONFIG.items()
        if status in config["allowed"]
    ]


def staff_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


@staff_required
def dashboard(request):
    counts = {item["status"]: item["total"] for item in Profile.objects.values("status").annotate(total=Count("id"))}
    membership_counts = {
        item["status"]: item["total"]
        for item in Membership.objects.values("status").annotate(total=Count("id"))
    }
    context = {
        "counts": counts,
        "membership_counts": membership_counts,
        "pending_memberships": Membership.objects.filter(
            status__in=(Membership.Status.SUBMITTED, Membership.Status.UNDER_REVIEW)
        ).select_related("user").order_by("submitted_at", "updated_at")[:8],
        "pending_profiles": Profile.objects.filter(status=Profile.Status.PENDING)
        .select_related("user")
        .order_by("updated_at")[:8],
    }
    return render(request, "moderation/dashboard.html", context)


@staff_required
def membership_list(request):
    selected_status = request.GET.get("status", Membership.Status.SUBMITTED)
    valid_statuses = {value for value, _label in Membership.Status.choices}
    memberships = Membership.objects.select_related("user").order_by("submitted_at", "updated_at")
    if selected_status in valid_statuses:
        memberships = memberships.filter(status=selected_status)
    else:
        selected_status = ""
    return render(
        request,
        "moderation/membership_list.html",
        {
            "memberships": memberships,
            "selected_status": selected_status,
            "status_choices": Membership.Status.choices,
        },
    )


@staff_required
def membership_review(request, pk):
    membership = get_object_or_404(
        Membership.objects.select_related("user", "user__profile").prefetch_related("decisions__actor"),
        pk=pk,
    )
    error = ""
    if request.method == "POST":
        try:
            moderate_membership(
                membership,
                request.user,
                request.POST.get("action", ""),
                request.POST.get("note", ""),
            )
        except (ValidationError, KeyError) as exception:
            error = (
                exception.messages[0]
                if isinstance(exception, ValidationError)
                else _("Decisão de adesão inválida.")
            )
        else:
            messages.success(request, _("Decisão de adesão registada."))
            return redirect("moderation:membership-list")
    allowed_actions = VALID_TRANSITIONS.get(membership.status, set()) & MEMBERSHIP_MODERATION_TARGETS
    actions = [
        (status, label)
        for status, label in Membership.Status.choices
        if status in allowed_actions
    ]
    return render(
        request,
        "moderation/membership_review.html",
        {"membership": membership, "actions": actions, "error": error},
    )


@staff_required
def profile_list(request):
    selected_status = request.GET.get("status", Profile.Status.PENDING)
    valid_statuses = {value for value, _label in Profile.Status.choices}
    profiles = Profile.objects.select_related("user", "reviewed_by").order_by("updated_at")
    if selected_status in valid_statuses:
        profiles = profiles.filter(status=selected_status)
    else:
        selected_status = ""
    return render(
        request,
        "moderation/profile_list.html",
        {"profiles": profiles, "selected_status": selected_status, "status_choices": Profile.Status.choices},
    )


@staff_required
def profile_review(request, pk):
    profile = get_object_or_404(
        Profile.objects.select_related("user", "reviewed_by").prefetch_related(
            "specializations", "skills", "experiences", "education_entries", "certifications", "languages"
        ),
        pk=pk,
    )
    error = ""
    if request.method == "POST":
        try:
            moderate_profile(profile, request.user, request.POST.get("action", ""), request.POST.get("reason", ""))
        except ValidationError as exception:
            error = exception.messages[0]
        else:
            messages.success(request, _("Decisão de moderação registada."))
            return redirect("moderation:profile-list")
    return render(
        request,
        "moderation/profile_review.html",
        {"profile": profile, "actions": available_profile_actions(profile.status), "error": error},
    )


@staff_required
def audit_list(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    events = AuditLog.objects.select_related("actor")
    action = request.GET.get("action", "").strip()
    if action:
        events = events.filter(action__icontains=action)
    return render(request, "moderation/audit_list.html", {"events": events[:200], "action": action})


@staff_required
def report_list(request):
    from interactions.models import Report

    selected_status = request.GET.get("status", Report.Status.OPEN)
    reports = Report.objects.select_related("reporter", "profile", "profile__user", "assigned_to")
    valid_statuses = {value for value, _label in Report.Status.choices}
    if selected_status in valid_statuses:
        reports = reports.filter(status=selected_status)
    else:
        selected_status = ""
    return render(
        request,
        "moderation/report_list.html",
        {"reports": reports, "selected_status": selected_status, "status_choices": Report.Status.choices},
    )


@staff_required
def report_review(request, pk):
    from interactions.models import Report

    report = get_object_or_404(
        Report.objects.select_related("reporter", "profile", "profile__user", "assigned_to"), pk=pk
    )
    error = ""
    if request.method == "POST":
        try:
            moderate_report(report, request.user, request.POST.get("action", ""), request.POST.get("note", ""))
        except ValidationError as exception:
            error = exception.messages[0]
        else:
            messages.success(request, _("Denúncia actualizada."))
            return redirect("moderation:report-list")
    return render(request, "moderation/report_review.html", {"report": report, "error": error})
