import importlib

from django.test import SimpleTestCase


normalize = importlib.import_module(
    "profiles.migrations.0008_normalize_existing_profile_text"
).normalize


class StoredProfileEncodingTests(SimpleTestCase):
    def test_known_corrupted_portuguese_terms_are_repaired(self):
        self.assertEqual(
            normalize("Universidade Cat??lica Portuguesa"),
            "Universidade Católica Portuguesa",
        )
        self.assertEqual(
            normalize("Tecnologias de Informa????o e Comunica????o"),
            "Tecnologias de Informação e Comunicação",
        )

    def test_snapshot_values_are_repaired_recursively(self):
        value = {
            "education": [{"qualification": "P??s-Gradua????o"}],
            "languages": ["Ingl??s", "Portugu??s"],
        }
        self.assertEqual(
            normalize(value),
            {
                "education": [{"qualification": "Pós-Graduação"}],
                "languages": ["Inglês", "Português"],
            },
        )
