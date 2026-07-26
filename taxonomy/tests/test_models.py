from django.db import IntegrityError, transaction
from django.test import TestCase

from taxonomy.models import Area, Sector, Skill, Specialization


class TaxonomyModelTests(TestCase):
    def test_hierarchy_connects_sector_area_and_specialization(self):
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        area = Area.objects.create(
            sector=sector,
            name="Desenvolvimento de software",
            slug="desenvolvimento-software",
        )
        specialization = Specialization.objects.create(
            area=area,
            name="Desenvolvimento Web",
            slug="desenvolvimento-web",
        )

        self.assertEqual(area.sector, sector)
        self.assertEqual(specialization.area, area)
        self.assertEqual(list(sector.areas.all()), [area])
        self.assertEqual(str(specialization), "Desenvolvimento Web")

    def test_skill_can_belong_to_multiple_specializations(self):
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        area = Area.objects.create(sector=sector, name="Software", slug="software")
        web = Specialization.objects.create(area=area, name="Web", slug="web")
        data = Specialization.objects.create(area=area, name="Dados", slug="dados")
        skill = Skill.objects.create(name="Python", slug="python")

        skill.specializations.add(web, data)

        self.assertCountEqual(skill.specializations.all(), [web, data])

    def test_slugs_are_unique(self):
        Sector.objects.create(name="Tecnologia", slug="tecnologia")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Sector.objects.create(name="Tecnologia B", slug="tecnologia")
