from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.db.utils import OperationalError
from django.shortcuts import redirect, render
from django.urls import reverse

from .features import active_features, locked_features


def home(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    return render(
        request,
        "core/home.html",
        {
            "canonical_url": request.build_absolute_uri(reverse("home")),
            "active_features": active_features(),
            "locked_features": locked_features(),
        },
    )


def robots(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = "\n".join(
        (
            "User-agent: *",
            "Allow: /",
            "Disallow: /conta/",
            "Disallow: /perfil/",
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
