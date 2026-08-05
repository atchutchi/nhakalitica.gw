from django.db import migrations, models


AVAILABILITY_LABELS = {
    "available": {"pt": "Disponível", "en": "Available", "fr": "Disponible"},
    "open": {"pt": "Aberto a propostas", "en": "Open to proposals", "fr": "Ouvert aux propositions"},
    "unavailable": {"pt": "Indisponível", "en": "Unavailable", "fr": "Indisponible"},
}
WORK_PREFERENCE_LABELS = {
    "onsite": {"pt": "Presencial", "en": "On-site", "fr": "Sur site"},
    "remote": {"pt": "Remoto", "en": "Remote", "fr": "À distance"},
    "hybrid": {"pt": "Híbrido", "en": "Hybrid", "fr": "Hybride"},
}
SENIORITY_LABELS = {
    "entry": {"pt": "Entrada", "en": "Entry level", "fr": "Débutant"},
    "junior": {"pt": "Júnior", "en": "Junior", "fr": "Junior"},
    "mid": {"pt": "Intermédio", "en": "Mid-level", "fr": "Intermédiaire"},
    "senior": {"pt": "Sénior", "en": "Senior", "fr": "Senior"},
    "lead": {"pt": "Liderança", "en": "Leadership", "fr": "Direction"},
}
LANGUAGE_LEVEL_LABELS = {
    "basic": {"pt": "Básico", "en": "Basic", "fr": "Élémentaire"},
    "intermediate": {"pt": "Intermédio", "en": "Intermediate", "fr": "Intermédiaire"},
    "advanced": {"pt": "Avançado", "en": "Advanced", "fr": "Avancé"},
    "fluent": {"pt": "Fluente", "en": "Fluent", "fr": "Courant"},
    "native": {"pt": "Nativo", "en": "Native", "fr": "Langue maternelle"},
}
LANGUAGE_LEVEL_CODES = {
    "Básico": "basic",
    "Intermédio": "intermediate",
    "Avançado": "advanced",
    "Fluente": "fluent",
    "Nativo": "native",
}

TAXONOMY_TRANSLATIONS = {
    "Sector": {
        "Tecnologias de Informação e Comunicação": (
            "Information and Communication Technologies",
            "Technologies de l’information et de la communication",
        ),
    },
    "Area": {
        "Desenvolvimento de Software": ("Software Development", "Développement logiciel"),
        "Gestão de Projectos Tecnológicos": ("Technology Project Management", "Gestion de projets technologiques"),
        "Transformação Digital": ("Digital Transformation", "Transformation numérique"),
    },
    "Specialization": {
        "Desenvolvimento Full Stack": ("Full Stack Development", "Développement full stack"),
        "Gestão de Projectos Digitais": ("Digital Project Management", "Gestion de projets numériques"),
        "Transformação Digital e Sistemas de Informação": (
            "Digital Transformation and Information Systems",
            "Transformation numérique et systèmes d’information",
        ),
    },
    "Skill": {
        "Comunicação digital": ("Digital communication", "Communication numérique"),
        "Gestao de projectos": ("Project management", "Gestion de projets"),
        "Gestão de fornecedores": ("Supplier management", "Gestion des fournisseurs"),
        "Gestão de projectos": ("Project management", "Gestion de projets"),
        "Gestão de risco": ("Risk management", "Gestion des risques"),
        "Gestão de sistemas de informação": ("Information systems management", "Gestion des systèmes d’information"),
        "Gestão ágil de backlog": ("Agile backlog management", "Gestion agile du backlog"),
        "Inteligência artificial": ("Artificial intelligence", "Intelligence artificielle"),
        "Monitorização e avaliação": ("Monitoring and evaluation", "Suivi et évaluation"),
        "Transformação digital": ("Digital transformation", "Transformation numérique"),
    },
}


def seed_taxonomy_translations(apps, schema_editor):
    for model_name, translations in TAXONOMY_TRANSLATIONS.items():
        Model = apps.get_model("taxonomy", model_name)
        for name, (name_en, name_fr) in translations.items():
            Model.objects.filter(name=name).update(name_en=name_en, name_fr=name_fr)


def localize_existing_snapshots(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    taxonomy_models = {
        "skills": apps.get_model("taxonomy", "Skill"),
        "specializations": apps.get_model("taxonomy", "Specialization"),
        "areas": apps.get_model("taxonomy", "Area"),
        "sectors": apps.get_model("taxonomy", "Sector"),
    }
    for profile in Profile.objects.exclude(published_snapshot={}):
        payload = dict(profile.published_snapshot)
        payload["availability_labels"] = AVAILABILITY_LABELS.get(
            payload.get("availability"),
            {},
        )
        payload["work_preference_labels"] = WORK_PREFERENCE_LABELS.get(
            payload.get("work_preference"),
            {},
        )
        payload["seniority_labels"] = SENIORITY_LABELS.get(
            payload.get("seniority_level"),
            {},
        )
        languages = []
        for item in payload.get("languages", []):
            translated = dict(item)
            level_code = translated.get("level_code", "") or LANGUAGE_LEVEL_CODES.get(
                translated.get("level", ""),
                "",
            )
            if level_code:
                translated["level_code"] = level_code
                translated["level_labels"] = LANGUAGE_LEVEL_LABELS.get(level_code, {})
            languages.append(translated)
        payload["languages"] = languages
        for key, Model in taxonomy_models.items():
            original_names = payload.get(key, [])
            records = {
                item.name: item
                for item in Model.objects.filter(name__in=original_names)
            }
            payload[f"{key}_i18n"] = {
                language: [
                    getattr(records.get(name), f"name_{language}", "") or name
                    for name in original_names
                ]
                for language in ("en", "fr")
            }
            payload[f"{key}_i18n"]["pt"] = original_names
        profile.published_snapshot = payload
        profile.save(update_fields=("published_snapshot",))


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0013_profile_show_organization_on_profile"),
        ("taxonomy", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sector",
            name="name_en",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em inglês"),
        ),
        migrations.AddField(
            model_name="sector",
            name="name_fr",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em francês"),
        ),
        migrations.AddField(
            model_name="area",
            name="name_en",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em inglês"),
        ),
        migrations.AddField(
            model_name="area",
            name="name_fr",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em francês"),
        ),
        migrations.AddField(
            model_name="specialization",
            name="name_en",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em inglês"),
        ),
        migrations.AddField(
            model_name="specialization",
            name="name_fr",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em francês"),
        ),
        migrations.AddField(
            model_name="skill",
            name="name_en",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em inglês"),
        ),
        migrations.AddField(
            model_name="skill",
            name="name_fr",
            field=models.CharField(blank=True, max_length=160, verbose_name="nome em francês"),
        ),
        migrations.RunPython(seed_taxonomy_translations, migrations.RunPython.noop),
        migrations.RunPython(localize_existing_snapshots, migrations.RunPython.noop),
    ]
