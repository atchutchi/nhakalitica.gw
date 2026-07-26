from datetime import date

from django.db import migrations


def _normalise_list(values):
    return [str(value).strip() for value in values if str(value or "").strip()]


def _infer_seniority(text):
    text = str(text or "").casefold()
    if any(term in text for term in ("director", "diretor", "chefe", "lead", "líder", "lider", "coordenador", "coordenadora")):
        return "lead"
    if any(term in text for term in ("sénior", "senior", "especialista", "consultor", "consultora")):
        return "senior"
    if any(term in text for term in ("júnior", "junior", "estagiário", "estagiaria", "assistente")):
        return "junior"
    return "mid"


def _experience_years(records):
    total_days = 0
    today = date.today()
    for record in records:
        start = record.get("start_date")
        if not start:
            continue
        end = record.get("end_date") or today.isoformat()
        start_date = date.fromisoformat(start) if isinstance(start, str) else start
        end_date = date.fromisoformat(end) if isinstance(end, str) else end
        total_days += max(0, (end_date - start_date).days)
    return max(1, round(total_days / 365)) if total_days else None


def _keywords_from_payload(payload):
    values = []
    for key in ("professional_title", "bio"):
        values.append(payload.get(key, ""))
    for key in ("skills", "specializations", "areas", "sectors"):
        values.extend(payload.get(key, []))
    for key in ("experiences", "education", "certifications", "languages"):
        for item in payload.get(key, []):
            if isinstance(item, dict):
                values.extend(item.values())
    return ", ".join(dict.fromkeys(_normalise_list(values)))


def backfill_profile_search_fields(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    for profile in Profile.objects.all():
        payload = profile.published_snapshot or {}
        public_title = payload.get("professional_title") or profile.professional_title
        public_bio = payload.get("bio") or profile.bio
        records = payload.get("experiences", [])

        if not records:
            records = [
                {
                    "title": item.title,
                    "organization": item.organization,
                    "description": item.description,
                    "start_date": item.start_date.isoformat() if item.start_date else "",
                    "end_date": item.end_date.isoformat() if item.end_date else "",
                }
                for item in profile.experiences.all()
            ]

        inferred_roles = public_title
        inferred_keywords = _keywords_from_payload(payload) if payload else ", ".join(
            dict.fromkeys(
                _normalise_list(
                    [
                        profile.professional_title,
                        profile.bio,
                        *profile.skills.values_list("name", flat=True),
                        *profile.specializations.values_list("name", flat=True),
                        *profile.specializations.values_list("area__name", flat=True),
                        *profile.specializations.values_list("area__sector__name", flat=True),
                    ]
                )
            )
        )
        inferred_years = _experience_years(records)
        inferred_seniority = _infer_seniority(" ".join([public_title, public_bio, inferred_keywords]))

        changed_fields = []
        if not profile.target_roles and inferred_roles:
            profile.target_roles = inferred_roles
            changed_fields.append("target_roles")
        if not profile.search_keywords and inferred_keywords:
            profile.search_keywords = inferred_keywords[:2000]
            changed_fields.append("search_keywords")
        if profile.years_experience is None and inferred_years is not None:
            profile.years_experience = inferred_years
            changed_fields.append("years_experience")
        if not profile.seniority_level:
            profile.seniority_level = inferred_seniority
            changed_fields.append("seniority_level")

        if payload:
            payload.setdefault("target_roles", inferred_roles)
            payload.setdefault("search_keywords", inferred_keywords[:2000])
            payload.setdefault("years_experience", profile.years_experience)
            payload.setdefault("seniority_level", profile.seniority_level)
            payload.setdefault("seniority_label", profile.get_seniority_level_display() if profile.seniority_level else "")
            profile.published_snapshot = payload
            changed_fields.append("published_snapshot")

        if changed_fields:
            profile.save(update_fields=sorted(set(changed_fields)))


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0009_profile_search_keywords"),
    ]

    operations = [
        migrations.RunPython(backfill_profile_search_fields, migrations.RunPython.noop),
    ]
