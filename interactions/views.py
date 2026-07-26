from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from urllib.parse import urlencode

from profiles.models import Profile
from profiles.selectors import public_profiles

from .forms import ContactRequestForm, FavoriteUpdateForm, ReportForm, SavedSearchForm
from .models import ContactRequest, Favorite, Notification, RecruitmentTag, SavedSearch
from .services import (
    build_shortlist_csv,
    add_favorite,
    clean_saved_search_params,
    create_contact,
    create_report,
    get_comparable_favorites,
    sync_favorite_tags,
    toggle_favorite,
    toggle_like,
)


def get_public_profile(slug):
    return get_object_or_404(public_profiles(), slug=slug)


@login_required
@require_POST
def favorite_toggle(request, slug):
    profile = get_public_profile(slug)
    added = toggle_favorite(request.user, profile)
    messages.success(request, "Perfil guardado." if added else "Perfil removido dos favoritos.")
    return redirect("public-profile", slug=profile.slug)


@login_required
@require_POST
def favorite_add(request, slug):
    profile = get_public_profile(slug)
    _favorite, created = add_favorite(request.user, profile)
    messages.success(request, "Perfil guardado." if created else "Perfil já está na shortlist.")
    return redirect("public-profile", slug=profile.slug)


@login_required
@require_POST
def like_toggle(request, slug):
    profile = get_public_profile(slug)
    added = toggle_like(request.user, profile)
    messages.success(request, "Gosto registado." if added else "Gosto removido.")
    return redirect("public-profile", slug=profile.slug)


@login_required
def contact(request, slug):
    profile = get_public_profile(slug)
    form = ContactRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_contact(
                request.user,
                profile,
                form.cleaned_data["subject"],
                form.cleaned_data["message"],
                request.META.get("REMOTE_ADDR", ""),
            )
        except ValidationError as exception:
            form.add_error(None, exception.messages[0])
        else:
            messages.success(request, "Pedido de contacto enviado com sucesso.")
            return redirect("interactions:contacts")
    return render(request, "interactions/contact_form.html", {"form": form, "profile": profile})


@login_required
def report(request, slug):
    profile = get_public_profile(slug)
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_report(
                request.user,
                profile,
                form.cleaned_data["reason"],
                form.cleaned_data["description"],
            )
        except ValidationError as exception:
            form.add_error(None, exception.messages[0])
        else:
            messages.success(request, "Denúncia enviada para análise.")
            return redirect("public-profile", slug=profile.slug)
    return render(request, "interactions/report_form.html", {"form": form, "profile": profile})


@login_required
def favorites(request):
    items = Favorite.objects.filter(
        user=request.user,
        profile__status__in=(Profile.Status.APPROVED, Profile.Status.CHANGES_PENDING),
        profile__is_public=True,
    ).select_related("profile", "profile__user").prefetch_related(
        Prefetch("tags", queryset=RecruitmentTag.objects.filter(user=request.user), to_attr="owned_tags")
    )
    active_status = request.GET.get("status", "")
    active_tag = request.GET.get("tag", "")
    if active_status in Favorite.Status.values:
        items = items.filter(status=active_status)
    else:
        active_status = ""
    if active_tag:
        items = items.filter(tags__name=active_tag, tags__user=request.user)
    return render(
        request,
        "interactions/favorites.html",
        {
            "favorites": items,
            "status_choices": Favorite.Status.choices,
            "tags": request.user.recruitment_tags.all(),
            "active_status": active_status,
            "active_tag": active_tag,
            "export_query": urlencode(
                {key: value for key, value in {"status": active_status, "tag": active_tag}.items() if value}
            ),
            "saved_searches": request.user.saved_searches.all(),
        },
    )


@login_required
@require_POST
@transaction.atomic
def favorite_update(request, pk):
    favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
    form = FavoriteUpdateForm(request.POST, instance=favorite)
    if form.is_valid():
        favorite = form.save()
        sync_favorite_tags(favorite, form.cleaned_data["tags"])
        messages.success(request, "Favorito actualizado.")
    else:
        messages.error(request, "Não foi possível actualizar o favorito.")
    return redirect("interactions:favorites")


@login_required
@require_POST
def saved_search_create(request):
    form = SavedSearchForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Não foi possível guardar a pesquisa.")
        return redirect("interactions:favorites")
    query_params = clean_saved_search_params(request.POST)
    saved_search = SavedSearch(user=request.user, name=form.cleaned_data["name"], query_params=query_params)
    try:
        saved_search.full_clean()
        saved_search.save()
    except ValidationError:
        messages.error(request, "Não foi possível guardar a pesquisa.")
        return redirect("interactions:favorites")
    messages.success(request, "Pesquisa guardada.")
    return redirect(f"{reverse('search')}?{urlencode(saved_search.query_params)}")


@login_required
@require_POST
def saved_search_delete(request, pk):
    saved_search = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    saved_search.delete()
    messages.success(request, "Pesquisa apagada.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("interactions:favorites")


@login_required
def saved_search_run(request, pk):
    saved_search = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    return redirect(f"{reverse('search')}?{urlencode(saved_search.query_params)}")


@login_required
def compare(request):
    favorites = get_comparable_favorites(request.user, request.GET.getlist("profiles"))
    return render(request, "interactions/compare.html", {"favorites": favorites})


@login_required
def shortlist_export(request):
    favorites = Favorite.objects.filter(user=request.user)
    active_status = request.GET.get("status", "")
    active_tag = request.GET.get("tag", "")
    if active_status in Favorite.Status.values:
        favorites = favorites.filter(status=active_status)
    if active_tag:
        favorites = favorites.filter(tags__name=active_tag, tags__user=request.user)
    response = HttpResponse(build_shortlist_csv(request.user, favorites), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="shortlist.csv"'
    return response


@login_required
def contacts(request):
    received = request.user.profile.contact_requests.select_related("sender")
    sent = request.user.sent_contact_requests.select_related("profile", "profile__user")
    return render(request, "interactions/contacts.html", {"received": received, "sent": sent})


@login_required
@require_POST
def contact_action(request, pk):
    contact_request = get_object_or_404(
        ContactRequest.objects.select_related("profile"), pk=pk, profile__user=request.user
    )
    action = request.POST.get("action")
    if action == "block":
        contact_request.status = ContactRequest.Status.BLOCKED
        message = "Contacto bloqueado."
    elif action == "report":
        contact_request.status = ContactRequest.Status.REPORTED
        message = "Contacto denunciado à administração."
        staff_ids = request.user.__class__.objects.filter(is_staff=True, is_active=True).values_list("id", flat=True)
        Notification.objects.bulk_create(
            [
                Notification(
                    user_id=user_id,
                    type="contact_reported",
                    title="Contacto denunciado",
                    body=f"O pedido de contacto #{contact_request.pk} foi denunciado.",
                    link="/admin/interactions/contactrequest/",
                )
                for user_id in staff_ids
            ]
        )
    else:
        messages.error(request, "Ação inválida.")
        return redirect("interactions:contacts")
    contact_request.save(update_fields=("status",))
    messages.success(request, message)
    return redirect("interactions:contacts")


@login_required
def notifications(request):
    return render(
        request,
        "interactions/notifications.html",
        {"notifications": request.user.notifications.all()[:100]},
    )


@login_required
@require_POST
def notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.read_at:
        notification.read_at = timezone.now()
        notification.save(update_fields=("read_at",))
    return redirect("interactions:notifications")
