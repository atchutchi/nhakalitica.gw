import json

from django.db import migrations


# The first local profile import was performed through a shell whose output
# encoding replaced non-ASCII bytes with question marks. Keep the repair
# deliberately narrow and idempotent so it only touches known Portuguese
# terms that are already corrupted in stored profile data.
REPLACEMENTS = {
    "Cat??lica": "Católica",
    "Informa????o": "Informação",
    "Comunica????o": "Comunicação",
    "Gest??o": "Gestão",
    "Guin??-Bissau": "Guiné-Bissau",
    "P??s-Gradua????o": "Pós-Graduação",
    "T??cnica": "Técnica",
    "Jur??dica": "Jurídica",
    "Forma????o": "Formação",
    "Pr??tico": "Prático",
    "Estagi??ria": "Estagiária",
    "An??lise": "Análise",
    "constitui????o": "constituição",
    "ac????es": "acções",
    "Franc??s": "Francês",
    "Ingl??s": "Inglês",
    "Portugu??s": "Português",
}


def normalize(value):
    if isinstance(value, str):
        for broken, fixed in REPLACEMENTS.items():
            value = value.replace(broken, fixed)
        return value
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    return value


def dedupe_dicts(items):
    result = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            result.append(item)
            continue
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def forwards(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Sector = apps.get_model("taxonomy", "Sector")
    Area = apps.get_model("taxonomy", "Area")
    Specialization = apps.get_model("taxonomy", "Specialization")
    Skill = apps.get_model("taxonomy", "Skill")
    Experience = apps.get_model("profiles", "Experience")
    Education = apps.get_model("profiles", "Education")
    Certification = apps.get_model("profiles", "Certification")
    ProfileLanguage = apps.get_model("profiles", "ProfileLanguage")

    for model in (Sector, Area, Specialization, Skill):
        for row in model.objects.all():
            fixed = normalize(row.name)
            if fixed != row.name:
                row.name = fixed
                row.save(update_fields=["name"])

    for model, fields in (
        (Experience, ("title", "organization", "location", "description")),
        (Education, ("institution", "qualification", "field_of_study", "description")),
        (Certification, ("name", "issuer")),
    ):
        for row in model.objects.all():
            changed = False
            for field in fields:
                value = getattr(row, field)
                fixed = normalize(value)
                if fixed != value:
                    setattr(row, field, fixed)
                    changed = True
            if changed:
                row.save(update_fields=list(fields))

    for row in list(ProfileLanguage.objects.all()):
        fixed = normalize(row.name)
        if fixed != row.name:
            duplicate = ProfileLanguage.objects.filter(profile_id=row.profile_id, name=fixed).exclude(pk=row.pk).first()
            if duplicate:
                row.delete()
            else:
                row.name = fixed
                row.save(update_fields=["name"])

    # Remove duplicate imported sections after normalizing their text. This
    # only removes exact duplicates for the same profile.
    for model, fields in (
        (Experience, ("profile_id", "title", "organization", "location", "description", "start_date", "end_date", "is_current")),
        (Education, ("profile_id", "institution", "qualification", "field_of_study", "start_date", "end_date", "description")),
    ):
        seen = set()
        for row in model.objects.order_by("pk"):
            key = tuple(getattr(row, field) for field in fields)
            if key in seen:
                row.delete()
            else:
                seen.add(key)

    for profile in Profile.objects.all():
        snapshot = normalize(profile.published_snapshot or {})
        if isinstance(snapshot, dict):
            for key in ("experiences", "education", "languages"):
                if isinstance(snapshot.get(key), list):
                    snapshot[key] = dedupe_dicts(snapshot[key])
        if snapshot != (profile.published_snapshot or {}):
            profile.published_snapshot = snapshot
            profile.save(update_fields=["published_snapshot"])


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0007_profile_cv_visibility_profile_location_is_public"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
