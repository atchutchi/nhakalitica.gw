from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _


def canonical_url(route_name):
    return f"{settings.PUBLIC_BASE_URL}{reverse(route_name)}"

def home(request):
    return render(
        request,
        "core/home.html",
        {
            "canonical_url": request.build_absolute_uri(reverse("home")),
        },
    )


def about(request):
    return render(
        request,
        "core/about.html",
        {"canonical_url": request.build_absolute_uri(reverse("about"))},
    )


def membership_types(request):
    return render(
        request,
        "core/membership_types.html",
        {"canonical_url": request.build_absolute_uri(reverse("membership-types"))},
    )


def how_it_works(request):
    return render(
        request,
        "core/how_it_works.html",
        {"canonical_url": request.build_absolute_uri(reverse("how-it-works"))},
    )


def legal_page(request, template_name, route_name):
    return render(
        request,
        template_name,
        {
            "canonical_url": canonical_url(route_name),
            "contact_email": settings.KALITICA_CONTACT_EMAIL,
            "legal_version": settings.LEGAL_DOCUMENT_VERSION,
            "legal_effective_date": _("5 de Agosto de 2026"),
        },
    )


def terms(request):
    return legal_page(request, "core/terms.html", "terms")


def privacy(request):
    return legal_page(request, "core/privacy.html", "privacy")


def code_of_conduct(request):
    return legal_page(request, "core/code_of_conduct.html", "code-of-conduct")


def robots(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = "\n".join(
        (
            "User-agent: *",
            "Allow: /",
            "Disallow: /conta/",
            "Disallow: /perfil/",
            "Disallow: /adesao/",
            "Disallow: /interacoes/",
            "Disallow: /administracao/",
            "Disallow: /admin/",
            "Disallow: /pesquisar/",
            f"Sitemap: {sitemap_url}",
        )
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
