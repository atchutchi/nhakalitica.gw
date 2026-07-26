from mimetypes import guess_type

from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from taxonomy.models import Area, Sector, Skill, Specialization

from .models import Profile
from .selectors import public_profiles


def search(request):
    paginator = Paginator(public_profiles(request.GET), 12)
    page = paginator.get_page(request.GET.get("page"))
    filter_params = request.GET.copy()
    filter_params.pop("page", None)
    context = {
        "page_obj": page,
        "filter_query": filter_params.urlencode(),
        "sectors": Sector.objects.filter(is_active=True),
        "areas": Area.objects.filter(is_active=True).select_related("sector"),
        "specializations": Specialization.objects.filter(is_active=True).select_related("area"),
        "skills": Skill.objects.filter(is_active=True),
        "availability_choices": Profile.Availability.choices,
        "work_preference_choices": Profile.WorkPreference.choices,
        "seniority_choices": Profile.Seniority.choices,
    }
    # Expor filtros ativos como etiquetas removíveis para que o recrutador
    # perceba rapidamente o contexto da pesquisa e possa ajustar um critério.
    labels = {
        "q": "Pesquisa",
        "sector": "Setor",
        "area": "Área",
        "specialization": "Especialização",
        "skill": "Competência",
        "location": "Localização",
        "availability": "Disponibilidade",
        "work_preference": "Modalidade",
        "seniority": "Nível",
        "language": "Idioma",
        "country": "País",
        "experience": "Experiência mínima",
        "cv": "Currículo disponível",
    }
    option_maps = {
        "sector": {item.slug: item.name for item in context["sectors"]},
        "area": {item.slug: item.name for item in context["areas"]},
        "specialization": {item.slug: item.name for item in context["specializations"]},
        "skill": {item.slug: item.name for item in context["skills"]},
        "availability": dict(Profile.Availability.choices),
        "work_preference": dict(Profile.WorkPreference.choices),
        "seniority": dict(Profile.Seniority.choices),
        "experience": {
            "1": "1 ano ou mais",
            "3": "3 anos ou mais",
            "5": "5 anos ou mais",
            "10": "10 anos ou mais",
        },
        "cv": {"1": "Currículo disponível"},
    }
    active_filters = []
    for parameter, label in labels.items():
        value = request.GET.get(parameter, "").strip()
        if not value:
            continue
        display_value = option_maps.get(parameter, {}).get(value, value)
        cleaned = request.GET.copy()
        cleaned.pop(parameter, None)
        cleaned.pop("page", None)
        active_filters.append({
            "label": label,
            "value": display_value,
            "remove_url": f"?{cleaned.urlencode()}" if cleaned else reverse("search"),
        })
    context["active_filters"] = active_filters
    return render(request, "profiles/search.html", context)


def public_profile(request, slug):
    profile = get_object_or_404(
        public_profiles(),
        slug=slug,
    )
    context = {
        "profile": profile,
        "display": profile.public_payload,
        "canonical_url": request.build_absolute_uri(reverse("public-profile", args=(profile.slug,))),
        "like_count": profile.profilelike_set.count(),
        "is_favorite": False,
        "is_liked": False,
    }
    if request.user.is_authenticated:
        context["is_favorite"] = profile.favorite_set.filter(user=request.user).exists()
        context["is_liked"] = profile.profilelike_set.filter(user=request.user).exists()
    return render(request, "profiles/public_detail.html", context)


def profile_photo(request, slug):
    profile = get_object_or_404(Profile.objects.select_related("user"), slug=slug)
    is_owner = request.user.is_authenticated and request.user == profile.user
    is_public = profile.is_public and profile.status in {
        Profile.Status.APPROVED,
        Profile.Status.CHANGES_PENDING,
    }
    if not is_owner and not is_public:
        raise Http404
    if not profile.photo:
        raise Http404
    response = FileResponse(
        profile.photo.open("rb"),
        content_type=guess_type(profile.photo.name)[0] or "image/jpeg",
    )
    response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


def profile_cv(request, slug):
    profile = get_object_or_404(Profile.objects.select_related("user"), slug=slug)
    is_owner = request.user.is_authenticated and request.user == profile.user
    is_public = profile.is_public and profile.status in {
        Profile.Status.APPROVED,
        Profile.Status.CHANGES_PENDING,
    }
    if not is_owner and not is_public:
        raise Http404
    can_access = (
        is_owner
        or profile.cv_visibility == Profile.CVVisibility.PUBLIC
        or (
            profile.cv_visibility == Profile.CVVisibility.MEMBERS
            and request.user.is_authenticated
        )
    )
    if not profile.cv_file or not can_access:
        raise Http404
    response = FileResponse(
        profile.cv_file.open("rb"),
        as_attachment=True,
        filename=f"curriculo-{profile.slug}.pdf",
        content_type="application/pdf",
    )
    response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response
