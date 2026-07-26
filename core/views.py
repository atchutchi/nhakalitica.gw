from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.db.utils import OperationalError
from django.shortcuts import render
from django.urls import reverse

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
