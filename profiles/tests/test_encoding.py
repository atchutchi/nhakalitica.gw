import importlib
import importlib.util

from django.test import SimpleTestCase


normalize = importlib.import_module(
    "profiles.migrations.0008_normalize_existing_profile_text"
).normalize


class StoredProfileEncodingTests(SimpleTestCase):
    def test_current_profile_import_corruption_is_repaired(self):
        module_name = "profiles.text_encoding"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        normalize_text = importlib.import_module(module_name).normalize_text

        self.assertEqual(normalize_text("Gest?o ?gil de backlog"), "Gestão ágil de backlog")
        self.assertEqual(
            normalize_text("Bissau, Guin?-Bissau"),
            "Bissau, Guiné-Bissau",
        )
        self.assertEqual(
            normalize_text("Tecnologias de Informa??o e Comunica??o"),
            "Tecnologias de Informação e Comunicação",
        )
        self.assertEqual(
            normalize_text("Gestão de sistemas de informa??o"),
            "Gestão de sistemas de informação",
        )
        self.assertEqual(
            normalize_text("Contribuir para a transforma??o digital"),
            "Contribuir para a transformação digital",
        )

    def test_current_profile_snapshot_corruption_is_repaired_recursively(self):
        module_name = "profiles.text_encoding"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        normalize_value = importlib.import_module(module_name).normalize_value

        value = {
            "location": "Guin?-Bissau",
            "skills": ["Intelig?ncia artificial", "Monitoriza??o e avalia??o"],
        }
        self.assertEqual(
            normalize_value(value),
            {
                "location": "Guiné-Bissau",
                "skills": ["Inteligência artificial", "Monitorização e avaliação"],
            },
        )

    def test_unaccented_demo_profile_text_is_repaired(self):
        module_name = "profiles.text_encoding"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        normalize_text = importlib.import_module(module_name).normalize_text

        self.assertEqual(normalize_text("Engenheiro de Petroleo"), "Engenheiro de Petróleo")
        self.assertEqual(
            normalize_text("Especialista em Saude Publica"),
            "Especialista em Saúde Pública",
        )
        self.assertEqual(
            normalize_text(
                "Experiencia profissional e colaboracao com projectos ligados a Guine-Bissau."
            ),
            "Experiência profissional e colaboração com projectos ligados à Guiné-Bissau.",
        )
        self.assertEqual(normalize_text("Ligacao profissional confirmada."), "Ligação profissional confirmada.")

    def test_profile_location_does_not_repeat_the_country(self):
        module_name = "profiles.text_encoding"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        normalize_location = importlib.import_module(module_name).normalize_location

        self.assertEqual(normalize_location("Bissau, Guin?-Bissau"), "Bissau")
        self.assertEqual(normalize_location("Bissau, Guiné-Bissau"), "Bissau")

    def test_published_snapshot_location_does_not_repeat_the_country(self):
        module_name = "profiles.text_encoding"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        normalize_profile_snapshot = importlib.import_module(
            module_name
        ).normalize_profile_snapshot

        self.assertEqual(
            normalize_profile_snapshot(
                {"location": "Bissau, Guiné-Bissau", "country": "Guiné-Bissau"}
            ),
            {"location": "Bissau", "country": "Guiné-Bissau"},
        )

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
