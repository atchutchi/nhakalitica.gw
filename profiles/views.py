from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CertificationForm,
    EducationForm,
    ExperienceForm,
    ProfileForm,
    ProfileLanguageForm,
)
from .models import Certification, Education, Experience, Profile, ProfileLanguage, ProfileRevision


SECTION_CONFIG = {
    "experiencia": (Experience, ExperienceForm, "Experiência profissional"),
    "formacao": (Education, EducationForm, "Formação"),
    "certificacao": (Certification, CertificationForm, "Certificação"),
    "idioma": (ProfileLanguage, ProfileLanguageForm, "Idioma"),
}


def mark_approved_profile_for_review(profile):
    if profile.status == Profile.Status.APPROVED:
        if not profile.published_snapshot:
            profile.published_snapshot = profile.build_public_snapshot()
            profile.published_at = profile.approved_at or timezone.now()
        profile.status = Profile.Status.CHANGES_PENDING
        profile.is_public = True


def record_pending_revision(profile):
    ProfileRevision.objects.update_or_create(
        profile=profile,
        status=ProfileRevision.Status.PENDING,
        defaults={"submitted_by": profile.user, "payload": profile.build_public_snapshot()},
    )


@login_required
def edit_profile(request):
    profile = request.user.profile
    was_approved = profile.status == Profile.Status.APPROVED
    previous_snapshot = profile.build_public_snapshot() if was_approved else None
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if was_approved:
            updated.published_snapshot = profile.published_snapshot or previous_snapshot
            updated.published_at = profile.published_at or profile.approved_at or timezone.now()
            updated.status = Profile.Status.CHANGES_PENDING
            updated.is_public = True
        if "cv_file" in request.FILES:
            updated.cv_uploaded_at = timezone.now()
        updated.save()
        form.save_m2m()
        if updated.status == Profile.Status.CHANGES_PENDING:
            record_pending_revision(updated)
        messages.success(request, "Perfil guardado com sucesso.")
        return redirect("accounts:dashboard")
    return render(request, "profiles/edit.html", {"form": form, "profile": profile})


@login_required
def submit_profile(request):
    if request.method != "POST":
        return redirect("accounts:dashboard")
    profile = request.user.profile
    required_consents = all(
        request.POST.get(name) == "on"
        for name in ("consent_profile_public", "consent_contact", "accept_terms", "accept_privacy")
    )
    if not request.user.email_verified_at:
        messages.error(request, "Confirma o teu email antes de submeter o perfil.")
    elif not profile.can_submit:
        messages.error(request, "Completa todas as secções obrigatórias antes de submeter.")
    elif not required_consents:
        messages.error(request, "Aceita os consentimentos obrigatórios antes de submeter.")
    else:
        now = timezone.now()
        profile.status = Profile.Status.PENDING
        profile.consent_profile_public = True
        profile.consent_contact = True
        profile.accepted_terms_version = "1.0"
        profile.accepted_terms_at = now
        profile.accepted_privacy_version = "1.0"
        profile.accepted_privacy_at = now
        profile.save()
        record_pending_revision(profile)
        from interactions.models import Notification

        staff_ids = request.user.__class__.objects.filter(is_staff=True, is_active=True).values_list("id", flat=True)
        Notification.objects.bulk_create(
            [
                Notification(
                    user_id=user_id,
                    type="profile_submitted",
                    title="Novo perfil para revisão",
                    body=f"{profile} submeteu o perfil.",
                    link="/administracao/perfis/?status=pending",
                )
                for user_id in staff_ids
            ]
        )
        messages.success(request, "Perfil submetido para revisão.")
    return redirect("accounts:dashboard")


def get_section_config(section):
    try:
        return SECTION_CONFIG[section]
    except KeyError as error:
        raise Http404 from error


@login_required
def add_section(request, section):
    _model, form_class, title = get_section_config(section)
    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.profile = request.user.profile
        mark_approved_profile_for_review(entry.profile)
        entry.profile.save()
        entry.save()
        if entry.profile.status == Profile.Status.CHANGES_PENDING:
            record_pending_revision(entry.profile)
        messages.success(request, f"{title} adicionada com sucesso.")
        return redirect("accounts:dashboard")
    return render(request, "profiles/section_form.html", {"form": form, "title": title})


@login_required
def edit_section(request, section, pk):
    model, form_class, title = get_section_config(section)
    entry = get_object_or_404(model, pk=pk, profile=request.user.profile)
    form = form_class(request.POST or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        profile = request.user.profile
        mark_approved_profile_for_review(profile)
        profile.save()
        form.save()
        if profile.status == Profile.Status.CHANGES_PENDING:
            record_pending_revision(profile)
        messages.success(request, f"{title} actualizada com sucesso.")
        return redirect("accounts:dashboard")
    return render(
        request,
        "profiles/section_form.html",
        {"form": form, "title": title, "is_editing": True},
    )


@login_required
def preview_profile(request):
    profile = request.user.profile
    return render(
        request,
        "profiles/public_detail.html",
        {"profile": profile, "display": profile.build_public_snapshot(), "like_count": 0, "is_preview": True},
    )


@login_required
def delete_section(request, section, pk):
    model, _form_class, title = get_section_config(section)
    entry = get_object_or_404(model, pk=pk, profile=request.user.profile)
    if request.method == "POST":
        profile = request.user.profile
        mark_approved_profile_for_review(profile)
        profile.save()
        entry.delete()
        if profile.status == Profile.Status.CHANGES_PENDING:
            record_pending_revision(profile)
        messages.success(request, f"{title} eliminada.")
        return redirect("accounts:dashboard")
    return render(request, "profiles/section_confirm_delete.html", {"entry": entry, "title": title})
