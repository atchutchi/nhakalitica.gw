from django.shortcuts import render
from django.urls import reverse


def csrf_failure(request, reason=""):
    return render(
        request,
        "403_csrf.html",
        {"retry_url": request.META.get("HTTP_REFERER") or reverse("home")},
        status=403,
    )
