"""Query helpers for the public directory.

Search intentionally operates on the approved payload for profiles with pending
changes.  This prevents an unreviewed edit from leaking into the public index,
while still allowing the relational taxonomy fields to be used for profiles
that have not yet received their first snapshot.
"""

import re
import unicodedata
from datetime import date

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils.text import slugify

from .models import Profile


_SYNONYMS = {
    "administracao": ("administracao", "administrativo", "assistente administrativo", "office manager"),
    "civil": ("civil", "construcao civil", "obras", "fiscalizacao", "engenharia civil"),
    "comunicacao": ("comunicacao", "comunicacao institucional", "relacoes publicas", "comunicacao social", "jornalismo"),
    "conteudo": ("conteudo", "conteudos", "criacao de conteudo", "social media", "multimedia"),
    "conteudos": ("conteudo", "conteudos", "criacao de conteudo", "social media", "multimedia"),
    "developer": ("developer", "programador", "desenvolvedor", "software engineer", "fullstack", "full stack"),
    "desenvolvedor": ("programador", "desenvolvedor", "developer", "software engineer", "fullstack", "full stack"),
    "direito": ("direito", "juridico", "juridica", "legal", "assessoria juridica"),
    "designer": ("designer", "design grafico", "web designer", "branding", "identidade visual"),
    "engenharia": ("engenharia", "engenheiro", "engenheira"),
    "engenheiro": ("engenheiro", "engenheira", "engenharia", "eng", "engenharia civil", "engenharia mecanica"),
    "energia": ("energia", "energias renovaveis", "agua", "saneamento"),
    "financas": ("financas", "financeiro", "credito", "contabilidade", "economia"),
    "gestao": ("gestao", "gestor", "gestora", "manager", "project manager", "projecto", "projeto"),
    "informatica": ("informatica", "informatico", "tecnologia da informacao", "tecnologia de informacao", "sistemas", "ti", "it"),
    "informatico": ("informatico", "informatica", "tecnico de informatica", "suporte tecnico", "administrador de sistemas", "ti", "it"),
    "juridica": ("juridica", "juridico", "direito", "legal", "assessoria juridica"),
    "marketing": ("marketing", "marketing digital", "vendas", "comercial", "branding"),
    "mecanico": ("mecanico", "mecanica", "engenharia mecanica", "engenheiro mecanico"),
    "medicina": ("medicina", "medico", "saude", "estudante de medicina"),
    "programador": ("programador", "desenvolvedor", "developer", "software engineer", "fullstack", "full stack"),
    "projeto": ("projeto", "projecto", "project manager", "gestao de projectos", "gestao de projetos"),
    "projecto": ("projeto", "projecto", "project manager", "gestao de projectos", "gestao de projetos"),
    "rh": ("rh", "recursos humanos"),
    "recursos": ("recursos", "recursos humanos"),
    "senior": ("senior", "senioridade", "lideranca", "lead", "chefe", "director"),
    "social": ("social", "social media", "redes sociais", "comunicacao digital"),
    "software": ("software", "programador", "desenvolvedor", "developer", "software engineer", "fullstack", "full stack", "desenvolvimento web", "desenvolvimento fullstack"),
    "ti": ("ti", "it", "tecnologia da informacao", "tecnologia de informacao", "informatica", "sistemas"),
}

_STOPWORDS = {
    "a",
    "as",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "area",
    "areas",
    "cargo",
    "cargos",
    "coisa",
    "coisas",
    "funcao",
    "funcoes",
    "funcionario",
    "funcionarios",
    "funcionaria",
    "funcionarias",
    "perfil",
    "perfis",
    "pessoa",
    "pessoas",
    "profissional",
    "profissionais",
    "talento",
    "talentos",
}
_SHORT_EXACT_TERMS = {"bi", "cv", "ia", "qa", "rh", "ti", "ui", "ux"}
_WORD_RE = re.compile(r"\w+", flags=re.UNICODE)


def _normalise(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in value if not unicodedata.combining(char)).casefold()


def _tokens(value):
    return [
        token
        for token in (_normalise(item) for item in _WORD_RE.findall(value or ""))
        if token and (token not in _STOPWORDS or token in _SHORT_EXACT_TERMS)
    ]


def _term_options(token):
    options = {token}
    if len(token) > 3 and token.endswith("s"):
        options.add(token.rstrip("s"))
    options.update(_SYNONYMS.get(token, ()))
    options.update(_SYNONYMS.get(token.rstrip("s"), ()))
    return tuple(sorted(options, key=len, reverse=True))


def _contains_option(text, option):
    option = _normalise(option).strip()
    if not option:
        return False
    if option in _SHORT_EXACT_TERMS or len(option) <= 2:
        return re.search(rf"(?<!\w){re.escape(option)}(?!\w)", text) is not None
    if " " in option:
        return option in text
    text_tokens = set(_tokens(text))
    if option in text_tokens:
        return True
    singular = option.rstrip("s") if len(option) > 3 else option
    if singular in text_tokens:
        return True
    return any(len(token) > 3 and token.rstrip("s") == singular for token in text_tokens)


def _snapshot_text(snapshot):
    if not snapshot:
        return ""
    values = [
        snapshot.get(key, "")
        for key in (
            "public_name",
            "professional_title",
            "bio",
            "target_roles",
            "search_keywords",
            "availability_label",
            "work_preference_label",
            "seniority_label",
        )
    ]
    if snapshot.get("location_is_public", False):
        values.append(snapshot.get("location", ""))
        values.append(snapshot.get("country", ""))
    for key in ("skills", "specializations", "areas", "sectors"):
        values.extend(snapshot.get(key, []))
    for key in ("experiences", "education", "certifications", "languages"):
        for item in snapshot.get(key, []):
            values.extend(item.values() if isinstance(item, dict) else [item])
    return " ".join(_normalise(value) for value in values)


def _profile_search_data(profile):
    """Return public searchable text and a relevance score for one profile."""
    payload = profile.published_snapshot or {}
    if payload:
        text = _snapshot_text(payload)
        title = _normalise(payload.get("professional_title"))
        location = _normalise(payload.get("location")) if payload.get("location_is_public", False) else ""
    else:
        values = [
            profile.public_name,
            profile.professional_title,
            profile.bio,
            profile.target_roles,
            profile.search_keywords,
            profile.get_availability_display(),
            profile.get_work_preference_display(),
            profile.get_seniority_level_display() if profile.seniority_level else "",
        ]
        if profile.location_is_public:
            values.extend((profile.location, profile.country))
        values.extend(profile.specializations.values_list("name", flat=True))
        values.extend(profile.specializations.values_list("area__name", flat=True))
        values.extend(profile.specializations.values_list("area__sector__name", flat=True))
        values.extend(profile.skills.values_list("name", flat=True))
        for experience in profile.experiences.all():
            values.extend((experience.title, experience.organization, experience.description))
        for education in profile.education_entries.all():
            values.extend((education.qualification, education.institution, education.field_of_study))
        for certification in profile.certifications.all():
            values.extend((certification.name, certification.issuer))
        values.extend(language.name for language in profile.languages.all())
        text = " ".join(_normalise(value) for value in values)
        title = _normalise(profile.professional_title)
        location = _normalise(profile.location) if profile.location_is_public else ""
    return text, title, location


def _query_matches(text, query):
    tokens = _tokens(query)
    if not tokens:
        return True
    return all(
        any(_contains_option(text, option) for option in _term_options(token))
        for token in tokens
    )


def _param(params, *names):
    for name in names:
        value = str(params.get(name, "")).strip()
        if value:
            return value
    return ""


def public_profiles(params=None):
    params = params or {}
    queryset = (
        Profile.objects.filter(
            Q(status=Profile.Status.APPROVED) | Q(status=Profile.Status.CHANGES_PENDING),
            is_public=True,
        )
        .select_related("user")
        .prefetch_related(
            "specializations__area__sector",
            "skills",
            "experiences",
            "education_entries",
            "certifications",
            "languages",
        )
    )

    query = str(params.get("q", "")).strip()
    relevance = {}
    if query:
        matches = []
        for profile in queryset:
            text, title, _ = _profile_search_data(profile)
            if _query_matches(text, query):
                matches.append(profile.pk)
                score = 0
                normalised_query = _normalise(query)
                if normalised_query and normalised_query in title:
                    score += 100
                payload = profile.published_snapshot or {}
                role_text = _normalise(payload.get("target_roles", profile.target_roles))
                keyword_text = _normalise(payload.get("search_keywords", profile.search_keywords))
                for token in _tokens(query):
                    options = _term_options(token)
                    if any(_contains_option(title, option) for option in options):
                        score += 25
                    if any(_contains_option(role_text, option) for option in options):
                        score += 20
                    if any(_contains_option(keyword_text, option) for option in options):
                        score += 15
                relevance[profile.pk] = score
        queryset = queryset.filter(pk__in=matches)

    filters = {
        "sector": "specializations__area__sector__slug",
        "area": "specializations__area__slug",
        "specialization": "specializations__slug",
        "skill": "skills__slug",
        "availability": "availability",
        "work_preference": "work_preference",
        "seniority": "seniority_level",
    }
    for parameter, field in filters.items():
        value = str(params.get(parameter, "")).strip()
        if not value:
            continue
        if parameter in {"availability", "work_preference", "seniority"}:
            snapshot_key = "seniority_level" if parameter == "seniority" else parameter
            queryset = queryset.filter(
                (Q(published_snapshot={}) & Q(**{field: value}))
                | Q(**{f"published_snapshot__{snapshot_key}": value})
            )
        else:
            matching_ids = []
            for profile in queryset:
                payload = profile.published_snapshot or {}
                if payload:
                    names = payload.get({
                        "sector": "sectors",
                        "area": "areas",
                        "specialization": "specializations",
                        "skill": "skills",
                    }[parameter], [])
                    if any(slugify(name) == value for name in names):
                        matching_ids.append(profile.pk)
                else:
                    relation = {
                        "sector": profile.specializations.filter(area__sector__slug=value),
                        "area": profile.specializations.filter(area__slug=value),
                        "specialization": profile.specializations.filter(slug=value),
                        "skill": profile.skills.filter(slug=value),
                    }[parameter]
                    if relation.exists():
                        matching_ids.append(profile.pk)
            queryset = queryset.filter(pk__in=matching_ids)

    location = _param(params, "location", "cidade", "city")
    if location:
        matching_ids = []
        for profile in queryset:
            _text, _title, public_location = _profile_search_data(profile)
            if _normalise(location) in public_location:
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    country = _param(params, "country", "pais")
    if country:
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            if payload:
                if not payload.get("location_is_public", False):
                    continue
                candidate = payload.get("country", "")
            elif profile.location_is_public:
                candidate = profile.country
            else:
                candidate = ""
            if _normalise(country) in _normalise(candidate):
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    language = _param(params, "language", "idioma")
    if language:
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            names = [item.get("name", "") for item in payload.get("languages", [])] if payload else profile.languages.values_list("name", flat=True)
            if any(slugify(name) == slugify(language) or _normalise(language) in _normalise(name) for name in names):
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    minimum_years = _param(params, "experience", "years_experience", "anos_experiencia")
    if minimum_years.isdigit():
        threshold = int(minimum_years)
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            declared_years = payload.get("years_experience") if payload else profile.years_experience
            if str(declared_years or "").isdigit() and int(declared_years) >= threshold:
                matching_ids.append(profile.pk)
                continue
            records = payload.get("experiences", []) if payload else profile.experiences.all()
            total_days = 0
            for record in records:
                start = record.get("start_date") if isinstance(record, dict) else record.start_date
                end = record.get("end_date") if isinstance(record, dict) else record.end_date
                if not start:
                    continue
                start_date = date.fromisoformat(start) if isinstance(start, str) else start
                end_date = date.fromisoformat(end) if isinstance(end, str) and end else (end or date.today())
                total_days += max(0, (end_date - start_date).days)
            if total_days >= threshold * 365:
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    if _param(params, "cv", "cv_available", "curriculo") in {"1", "true", "yes", "sim"}:
        queryset = queryset.filter(cv_file__isnull=False).exclude(cv_file="").exclude(cv_visibility=Profile.CVVisibility.PRIVATE)

    ordering = str(params.get("order", "relevance"))
    if query and ordering in {"relevance", ""} and relevance:
        whens = [When(pk=pk, then=Value(score)) for pk, score in relevance.items()]
        queryset = queryset.annotate(_relevance=Case(*whens, default=Value(0), output_field=IntegerField())).order_by("-_relevance", "-updated_at", "public_name")
    elif ordering in {"name", "name_asc"}:
        queryset = queryset.order_by("public_name", "pk")
    elif ordering == "name_desc":
        queryset = queryset.order_by("-public_name", "-pk")
    elif ordering in {"experience", "most_experience"}:
        queryset = queryset.order_by("-experiences__start_date", "public_name")
    else:
        queryset = queryset.order_by("-updated_at", "public_name", "pk")
    return queryset.distinct()
