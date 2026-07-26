from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from profiles.models import Profile

from .models import AuditLog
from .services import ACTION_CONFIG, moderate_profile, moderate_report


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
    context = {
        "counts": counts,
        "pending_profiles": Profile.objects.filter(status=Profile.Status.PENDING)
        .select_related("user")
        .order_by("updated_at")[:8],
    }
    return render(request, "moderation/dashboard.html", context)


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
            messages.success(request, "Decisão de moderação registada.")
            return redirect("moderation:profile-list")
    return render(
        request,
        "moderation/profile_review.html",
        {"profile": profile, "actions": ACTION_CONFIG, "error": error},
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
            messages.success(request, "Denúncia actualizada.")
            return redirect("moderation:report-list")
    return render(request, "moderation/report_review.html", {"report": report, "error": error})
