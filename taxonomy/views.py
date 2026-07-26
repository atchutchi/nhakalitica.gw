from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from profiles.selectors import public_profiles

from .models import Area


def area_list(request):
    areas = Area.objects.filter(is_active=True).select_related("sector")
    return render(
        request,
        "taxonomy/area_list.html",
        {"areas": areas, "canonical_url": request.build_absolute_uri(reverse("area-list"))},
    )


def area_detail(request, slug):
    area = get_object_or_404(
        Area.objects.filter(is_active=True).select_related("sector").prefetch_related("specializations"),
        slug=slug,
    )
    profiles = public_profiles({"area": area.slug})
    return render(
        request,
        "taxonomy/area_detail.html",
        {
            "area": area,
            "profiles": profiles,
            "canonical_url": request.build_absolute_uri(reverse("area-detail", args=(area.slug,))),
        },
    )
