from django.db import migrations


REPLACEMENTS = {
    "Engenheiro de Petroleo": "Engenheiro de Petróleo",
    "Especialista em Saude Publica": "Especialista em Saúde Pública",
    "Experiencia profissional e colaboracao com projectos ligados a Guine-Bissau.": (
        "Experiência profissional e colaboração com projectos ligados à Guiné-Bissau."
    ),
    "Ligacao profissional confirmada.": "Ligação profissional confirmada.",
    "Guine-Bissau": "Guiné-Bissau",
    "Cat?lica": "Católica",
    "Informa??o": "Informação",
    "informa??o": "informação",
    "Comunica??o": "Comunicação",
    "Transforma??o": "Transformação",
    "transforma??o": "transformação",
    "Gest?o": "Gestão",
    "?gil": "ágil",
    "Guin?-Bissau": "Guiné-Bissau",
    "Tecnol?gicos": "Tecnológicos",
    "Intelig?ncia": "Inteligência",
    "Monitoriza??o": "Monitorização",
    "avalia??o": "avaliação",
    "Ades?o": "Adesão",
    "cria??o": "criação",
    "liga??o": "ligação",
    "colabora??o": "colaboração",
    "Franc?s": "Francês",
    "Ingl?s": "Inglês",
    "Portugu?s": "Português",
    "ligadas ? Guiné-Bissau": "ligadas à Guiné-Bissau",
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


def normalize_location(value):
    value = normalize(value)
    if value.strip().casefold() == "bissau, guiné-bissau".casefold():
        return "Bissau"
    return value


def normalize_profile_snapshot(value):
    value = normalize(value)
    if isinstance(value, dict) and "location" in value:
        value["location"] = normalize_location(value["location"])
    return value


def repair_fields(model, fields):
    for row in model.objects.all():
        changed = []
        for field in fields:
            value = getattr(row, field)
            fixed = normalize(value)
            if fixed != value:
                setattr(row, field, fixed)
                changed.append(field)
        if changed:
            row.save(update_fields=changed)


def forwards(apps, schema_editor):
    for model_name in ("Sector", "Area", "Specialization", "Skill"):
        repair_fields(apps.get_model("taxonomy", model_name), ("name",))

    Profile = apps.get_model("profiles", "Profile")
    repair_fields(
        Profile,
        (
            "public_name",
            "professional_title",
            "bio",
            "target_roles",
            "search_keywords",
            "location",
            "country",
            "review_note",
            "published_snapshot",
        ),
    )
    for profile in Profile.objects.exclude(location=""):
        fixed_location = normalize_location(profile.location)
        if fixed_location != profile.location:
            profile.location = fixed_location
            profile.save(update_fields=["location"])
    for profile in Profile.objects.exclude(published_snapshot={}):
        fixed_snapshot = normalize_profile_snapshot(profile.published_snapshot)
        if fixed_snapshot != profile.published_snapshot:
            profile.published_snapshot = fixed_snapshot
            profile.save(update_fields=["published_snapshot"])
    repair_fields(
        apps.get_model("profiles", "ProfileRevision"),
        ("payload", "review_note"),
    )
    repair_fields(
        apps.get_model("profiles", "Experience"),
        ("title", "organization", "location", "description"),
    )
    repair_fields(
        apps.get_model("profiles", "Education"),
        ("institution", "qualification", "field_of_study", "description"),
    )
    repair_fields(
        apps.get_model("profiles", "Certification"),
        ("name", "issuer"),
    )
    repair_fields(apps.get_model("profiles", "ProfileLanguage"), ("name",))
    repair_fields(
        apps.get_model("memberships", "Membership"),
        ("relationship_note", "motivation"),
    )
    repair_fields(
        apps.get_model("memberships", "MembershipDecision"),
        ("note",),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("memberships", "0002_membership_accepts_code_of_conduct_and_more"),
        ("profiles", "0011_profile_is_discoverable_profile_review_status"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
