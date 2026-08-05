from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import translation
from importlib import import_module

from memberships.models import Membership
from taxonomy.models import Area, Sector, Skill, Specialization


class TaxonomyLocalizationTests(TestCase):
    def test_localized_name_uses_active_language_and_portuguese_fallback(self):
        sector = Sector.objects.create(
            name="Saúde",
            name_en="Health",
            name_fr="",
            slug="saude",
        )

        with translation.override("en"):
            self.assertEqual(sector.localized_name, "Health")
        with translation.override("fr"):
            self.assertEqual(sector.localized_name, "Saúde")

    def test_all_taxonomy_models_expose_localized_name(self):
        sector = Sector.objects.create(name="Tecnologia", name_en="Technology", slug="tecnologia")
        area = Area.objects.create(
            sector=sector,
            name="Software",
            name_fr="Logiciel",
            slug="software",
        )
        specialization = Specialization.objects.create(
            area=area,
            name="Desenvolvimento Web",
            name_en="Web Development",
            slug="web",
        )
        skill = Skill.objects.create(name="Gestão", name_fr="Gestion", slug="gestao")

        with translation.override("en"):
            self.assertEqual(area.localized_name, "Software")
            self.assertEqual(specialization.localized_name, "Web Development")
        with translation.override("fr"):
            self.assertEqual(area.localized_name, "Logiciel")
            self.assertEqual(skill.localized_name, "Gestion")

    def test_public_snapshot_exposes_choice_labels_for_all_languages(self):
        user = get_user_model().objects.create_user(
            email="snapshot-language@example.com",
            password="PalavraPasseSegura2026!",
        )
        user.membership.status = Membership.Status.APPROVED
        user.membership.save(update_fields=("status",))
        profile = user.profile
        profile.availability = profile.Availability.OPEN
        profile.work_preference = profile.WorkPreference.HYBRID
        profile.seniority_level = profile.Seniority.SENIOR
        profile.save()
        skill = Skill.objects.create(
            name="Gestão de risco",
            name_en="Risk management",
            name_fr="Gestion des risques",
            slug="gestao-risco-snapshot",
        )
        profile.skills.add(skill)

        payload = profile.build_public_snapshot()

        self.assertEqual(payload["availability_labels"]["pt"], "Aberto a propostas")
        self.assertEqual(payload["availability_labels"]["en"], "Open to proposals")
        self.assertEqual(payload["availability_labels"]["fr"], "Ouvert aux propositions")
        self.assertEqual(payload["work_preference_labels"]["en"], "Hybrid")
        self.assertEqual(payload["seniority_labels"]["fr"], "Senior")
        self.assertEqual(payload["skills_i18n"]["en"], ["Risk management"])
        profile.published_snapshot = payload
        with translation.override("fr"):
            self.assertEqual(profile.public_payload["availability_label"], "Ouvert aux propositions")
            self.assertEqual(profile.public_skill_names, ["Gestion des risques"])

    def test_snapshot_migration_infers_legacy_language_level(self):
        user = get_user_model().objects.create_user(
            email="legacy-snapshot@example.com",
            password="PalavraPasseSegura2026!",
        )
        profile = user.profile
        profile.published_snapshot = {
            "availability": "open",
            "work_preference": "hybrid",
            "seniority_level": "senior",
            "languages": [{"name": "Português", "level": "Fluente"}],
        }
        profile.save(update_fields=("published_snapshot",))
        migration = import_module("taxonomy.migrations.0002_localized_names")

        class Apps:
            @staticmethod
            def get_model(app_label, model_name):
                models = {
                    ("profiles", "Profile"): type(profile),
                    ("taxonomy", "Skill"): Skill,
                    ("taxonomy", "Specialization"): Specialization,
                    ("taxonomy", "Area"): Area,
                    ("taxonomy", "Sector"): Sector,
                }
                return models[(app_label, model_name)]

        migration.localize_existing_snapshots(Apps(), None)
        profile.refresh_from_db()

        language = profile.published_snapshot["languages"][0]
        self.assertEqual(language["level_code"], "fluent")
        self.assertEqual(language["level_labels"]["en"], "Fluent")
