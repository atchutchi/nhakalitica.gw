from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import MembershipApplicationForm
from .models import Membership
from .services import transition_membership


def get_or_create_membership(user):
    membership, _created = Membership.objects.get_or_create(user=user)
    return membership


def submission_errors(user, membership):
    errors = []
    if not user.email_verified_at:
        errors.append(_("Confirma o teu email antes de submeter a candidatura."))
    if not membership.member_type:
        errors.append(_("Escolhe o tipo de adesão."))
    if not membership.relationship:
        errors.append(_("Indica a tua ligação à Guiné-Bissau."))
    if (
        membership.relationship == Membership.Relationship.RELEVANT_LINK
        and not membership.relationship_note.strip()
    ):
        errors.append(_("Explica a tua ligação relevante à Guiné-Bissau."))
    if not membership.motivation.strip():
        errors.append(_("Explica a tua motivação para aderir."))
    if not all(
        (
            membership.accepts_code_of_conduct,
            membership.accepts_privacy,
            membership.confirms_truth,
        )
    ):
        errors.append(_("Aceita os consentimentos obrigatórios."))

    profile = user.profile
    if not all(
        value.strip()
        for value in (
            profile.public_name,
            profile.professional_title,
            profile.bio,
        )
    ):
        errors.append(_("Completa o nome, título e resumo do perfil profissional."))
    return errors


def application_progress(user, membership):
    profile = user.profile
    relationship_complete = bool(membership.relationship) and bool(
        membership.relationship != Membership.Relationship.RELEVANT_LINK
        or membership.relationship_note.strip()
    )
    professional_complete = all(
        value.strip()
        for value in (
            profile.public_name,
            profile.professional_title,
            profile.bio,
        )
    )
    privacy_complete = all(
        (
            membership.accepts_code_of_conduct,
            membership.accepts_privacy,
            membership.confirms_truth,
        )
    )
    review_complete = bool(
        membership.member_type
        and relationship_complete
        and professional_complete
        and membership.motivation.strip()
        and privacy_complete
    )
    submitted = membership.status not in {
        Membership.Status.DRAFT,
        Membership.Status.CORRECTIONS_REQUIRED,
    }
    steps = (
        {"label": _("Escolher o tipo de adesão"), "complete": bool(membership.member_type), "route": "memberships:edit"},
        {"label": _("Ligação à Guiné-Bissau e elegibilidade"), "complete": relationship_complete, "route": "memberships:edit"},
        {"label": _("Perfil profissional"), "complete": professional_complete, "route": "profiles:edit"},
        {"label": _("Privacidade e visibilidade"), "complete": privacy_complete, "route": "memberships:edit"},
        {"label": _("Rever e confirmar"), "complete": review_complete, "route": "memberships:review"},
        {"label": _("Submeter candidatura"), "complete": submitted, "route": "memberships:review"},
    )
    completed_count = sum(step["complete"] for step in steps)
    return {
        "application_steps": steps,
        "completed_count": completed_count,
        "progress_percent": round(completed_count / len(steps) * 100),
        "latest_decision": membership.decisions.first(),
    }


@login_required
def dashboard(request):
    membership = get_or_create_membership(request.user)
    context = {"membership": membership}
    context.update(application_progress(request.user, membership))
    return render(
        request,
        "memberships/dashboard.html",
        context,
    )


@login_required
def edit(request):
    membership = get_or_create_membership(request.user)
    if not membership.can_edit_application:
        messages.info(request, _("A candidatura está bloqueada enquanto decorre a análise."))
        return redirect("memberships:dashboard")

    form = MembershipApplicationForm(request.POST or None, instance=membership)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Rascunho da candidatura guardado."))
        return redirect("memberships:dashboard")
    context = {"form": form, "membership": membership}
    context.update(application_progress(request.user, membership))
    return render(
        request,
        "memberships/application_form.html",
        context,
    )


@login_required
def review(request):
    membership = get_or_create_membership(request.user)
    context = {
        "membership": membership,
        "submission_errors": submission_errors(request.user, membership),
    }
    context.update(application_progress(request.user, membership))
    return render(
        request,
        "memberships/application_review.html",
        context,
    )


@login_required
@require_POST
def submit(request):
    membership = get_or_create_membership(request.user)
    if not membership.can_edit_application:
        messages.info(request, _("A candidatura já foi submetida."))
        return redirect("memberships:dashboard")

    errors = submission_errors(request.user, membership)
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect("memberships:review")

    transition_membership(
        membership,
        request.user,
        Membership.Status.SUBMITTED,
    )
    messages.success(request, _("Candidatura submetida para análise."))
    return redirect("memberships:dashboard")
