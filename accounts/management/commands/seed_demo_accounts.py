import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import LegalAcceptance, User
from memberships.models import Membership
from profiles.models import Education, Experience, Profile, ProfileLanguage
from taxonomy.models import Area, Sector, Skill, Specialization


DEMO_ACCOUNTS = (
    {
        "email": "admin.rede@demo.nhakalitica.gw",
        "password_env": "DEMO_ADMIN_1_PASSWORD",
        "first_name": "Administração",
        "last_name": "Kalitica",
        "public_name": "Administração da Rede (Demonstração)",
        "professional_title": "Gestão da plataforma e adesões",
        "bio": "Conta de demonstração da equipa responsável pela administração da rede Kalitica.",
        "location": "Bissau",
        "country": "Guiné-Bissau",
        "member_type": Membership.Type.EFFECTIVE,
        "relationship": Membership.Relationship.CITIZEN,
        "is_admin": True,
    },
    {
        "email": "admin.moderacao@demo.nhakalitica.gw",
        "password_env": "DEMO_ADMIN_2_PASSWORD",
        "first_name": "Moderação",
        "last_name": "Kalitica",
        "public_name": "Moderação Kalitica (Demonstração)",
        "professional_title": "Moderação e acompanhamento de membros",
        "bio": "Conta de demonstração da equipa que analisa adesões e acompanha a comunidade Kalitica.",
        "location": "Lisboa",
        "country": "Portugal",
        "member_type": Membership.Type.OBSERVER,
        "relationship": Membership.Relationship.DIASPORA,
        "is_admin": True,
    },
    {
        "email": "membro.bissau@demo.nhakalitica.gw",
        "password_env": "DEMO_MEMBER_1_PASSWORD",
        "first_name": "Membro",
        "last_name": "Bissau",
        "public_name": "Membro de Bissau (Demonstração)",
        "professional_title": "Coordenação de programas comunitários",
        "bio": "Perfil fictício criado exclusivamente para demonstrar a experiência de um membro aprovado em Bissau.",
        "location": "Bissau",
        "country": "Guiné-Bissau",
        "member_type": Membership.Type.EFFECTIVE,
        "relationship": Membership.Relationship.CITIZEN,
        "is_admin": False,
    },
    {
        "email": "membro.diaspora@demo.nhakalitica.gw",
        "password_env": "DEMO_MEMBER_2_PASSWORD",
        "first_name": "Membro",
        "last_name": "Diáspora",
        "public_name": "Membro da Diáspora (Demonstração)",
        "professional_title": "Gestão de parcerias e cooperação",
        "bio": "Perfil fictício criado exclusivamente para demonstrar a experiência de um membro aprovado da diáspora.",
        "location": "Paris",
        "country": "França",
        "member_type": Membership.Type.OBSERVER,
        "relationship": Membership.Relationship.DIASPORA,
        "is_admin": False,
    },
)


class Command(BaseCommand):
    help = "Cria as contas aprovadas do ambiente de demonstração."

    @staticmethod
    def enabled():
        return os.getenv("DEMO_SEED_ENABLED", "False").lower() in {"1", "true", "yes"}

    def handle(self, *args, **options):
        if not self.enabled():
            self.stdout.write("Criação das contas de demonstração desactivada.")
            return

        missing = [item["password_env"] for item in DEMO_ACCOUNTS if not os.getenv(item["password_env"])]
        if missing:
            raise CommandError(
                "Faltam as palavras-passe obrigatórias das contas de demonstração: "
                + ", ".join(missing)
            )

        with transaction.atomic():
            sector, _ = Sector.objects.update_or_create(
                slug="gestao-e-desenvolvimento",
                defaults={
                    "name": "Gestão e desenvolvimento",
                    "name_en": "Management and development",
                    "name_fr": "Gestion et développement",
                    "is_active": True,
                },
            )
            area, _ = Area.objects.update_or_create(
                slug="gestao-de-comunidades",
                defaults={
                    "sector": sector,
                    "name": "Gestão de comunidades",
                    "name_en": "Community management",
                    "name_fr": "Gestion de communautés",
                    "is_active": True,
                },
            )
            specialization, _ = Specialization.objects.update_or_create(
                slug="redes-profissionais",
                defaults={
                    "area": area,
                    "name": "Redes profissionais",
                    "name_en": "Professional networks",
                    "name_fr": "Réseaux professionnels",
                    "is_active": True,
                },
            )
            skills = []
            for slug, names in (
                (
                    "gestao-de-comunidades",
                    ("Gestão de comunidades", "Community management", "Gestion de communautés"),
                ),
                (
                    "cooperacao-institucional",
                    ("Cooperação institucional", "Institutional cooperation", "Coopération institutionnelle"),
                ),
            ):
                skill, _ = Skill.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": names[0],
                        "name_en": names[1],
                        "name_fr": names[2],
                        "is_active": True,
                    },
                )
                skill.specializations.add(specialization)
                skills.append(skill)

            now = timezone.now()
            for item in DEMO_ACCOUNTS:
                user, _ = User.objects.update_or_create(
                    email=item["email"],
                    defaults={
                        "first_name": item["first_name"],
                        "last_name": item["last_name"],
                        "is_active": True,
                        "is_staff": item["is_admin"],
                        "is_superuser": item["is_admin"],
                        "email_verified_at": now,
                    },
                )
                user.set_password(os.environ[item["password_env"]])
                user.save(update_fields=("password",))

                Membership.objects.update_or_create(
                    user=user,
                    defaults={
                        "member_type": item["member_type"],
                        "relationship": item["relationship"],
                        "motivation": "Conta criada para a demonstração interna da plataforma.",
                        "accepts_code_of_conduct": True,
                        "accepts_privacy": True,
                        "confirms_truth": True,
                        "status": Membership.Status.APPROVED,
                        "submitted_at": now,
                        "decided_at": now,
                    },
                )

                profile, _ = Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "public_name": item["public_name"],
                        "professional_title": item["professional_title"],
                        "bio": item["bio"],
                        "target_roles": item["professional_title"],
                        "search_keywords": "Kalitica, Guiné-Bissau, comunidade, cooperação",
                        "location": item["location"],
                        "country": item["country"],
                        "years_experience": 5,
                        "seniority_level": Profile.Seniority.SENIOR,
                        "availability": Profile.Availability.OPEN,
                        "work_preference": Profile.WorkPreference.HYBRID,
                        "contact_visibility": Profile.ContactVisibility.FORM,
                        "status": Profile.Status.APPROVED,
                        "review_status": Profile.ReviewStatus.APPROVED,
                        "is_public": True,
                        "is_discoverable": True,
                        "approved_at": now,
                        "reviewed_at": now,
                        "reviewed_by": user,
                        "published_at": now,
                        "consent_profile_public": True,
                        "consent_contact": True,
                        "accepted_terms_version": settings.LEGAL_DOCUMENT_VERSION,
                        "accepted_terms_at": now,
                        "accepted_privacy_version": settings.LEGAL_DOCUMENT_VERSION,
                        "accepted_privacy_at": now,
                    },
                )
                profile.specializations.set((specialization,))
                profile.skills.set(skills)
                Experience.objects.update_or_create(
                    profile=profile,
                    title=item["professional_title"],
                    organization="Kalitica Networking Society",
                    defaults={
                        "location": item["location"],
                        "description": "Experiência fictícia para demonstração da plataforma.",
                        "start_date": date(2021, 1, 1),
                        "is_current": True,
                    },
                )
                Education.objects.update_or_create(
                    profile=profile,
                    institution="Instituição de Demonstração",
                    qualification="Formação em gestão e cooperação",
                    defaults={
                        "field_of_study": "Gestão",
                        "end_date": date(2020, 7, 1),
                    },
                )
                ProfileLanguage.objects.update_or_create(
                    profile=profile,
                    name="Português",
                    defaults={"level": ProfileLanguage.Level.FLUENT},
                )
                profile.published_snapshot = profile.build_public_snapshot()
                profile.save(update_fields=("published_snapshot", "updated_at"))

                for document_type in (
                    LegalAcceptance.DocumentType.TERMS,
                    LegalAcceptance.DocumentType.PRIVACY,
                    LegalAcceptance.DocumentType.CODE,
                ):
                    LegalAcceptance.objects.get_or_create(
                        user=user,
                        document_type=document_type,
                        version=settings.LEGAL_DOCUMENT_VERSION,
                        source=LegalAcceptance.Source.PROFILE,
                    )

        self.stdout.write(self.style.SUCCESS("Quatro contas de demonstração preparadas."))
