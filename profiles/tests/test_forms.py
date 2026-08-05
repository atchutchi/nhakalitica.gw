from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.forms import CertificationForm, EducationForm, ExperienceForm, ProfileForm


class ProfileFormTests(TestCase):
    def test_organization_visibility_is_only_offered_to_representatives(self):
        user = get_user_model().objects.create_user(
            email="representative@example.com",
            password="PalavraPasseSegura2026!",
        )

        private_form = ProfileForm(instance=user.profile)
        self.assertNotIn("show_organization_on_profile", private_form.fields)

        user.membership.represents_organization = True
        user.membership.save(update_fields=("represents_organization",))
        representative_form = ProfileForm(instance=user.profile)
        self.assertIn("show_organization_on_profile", representative_form.fields)

    def test_accepts_pdf_up_to_ten_megabytes(self):
        upload = SimpleUploadedFile("curriculo.pdf", b"%PDF-1.4\nconteudo", "application/pdf")
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertNotIn("cv_file", form.errors)

    def test_rejects_non_pdf_file(self):
        upload = SimpleUploadedFile("curriculo.txt", b"conteudo", "text/plain")
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertIn("cv_file", form.errors)

    def test_rejects_pdf_above_ten_megabytes(self):
        upload = SimpleUploadedFile(
            "curriculo.pdf",
            b"%PDF" + (b"x" * (10 * 1024 * 1024)),
            "application/pdf",
        )
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertIn("cv_file", form.errors)

    def test_experience_end_date_cannot_precede_start_date(self):
        form = ExperienceForm(
            data={
                "title": "Programadora",
                "organization": "CVLink",
                "start_date": "2025-02-01",
                "end_date": "2025-01-01",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_current_experience_cannot_have_end_date(self):
        form = ExperienceForm(
            data={
                "title": "Programadora",
                "organization": "CVLink",
                "start_date": "2025-01-01",
                "end_date": "2025-02-01",
                "is_current": "on",
            }
        )
        self.assertFalse(form.is_valid())

    def test_education_and_certification_validate_date_order(self):
        education = EducationForm(
            data={
                "institution": "Universidade",
                "qualification": "Licenciatura",
                "start_date": "2025-02-01",
                "end_date": "2025-01-01",
            }
        )
        certification = CertificationForm(
            data={
                "name": "Certificação",
                "issuer": "Entidade",
                "issue_date": "2025-02-01",
                "expiry_date": "2025-01-01",
            }
        )
        self.assertFalse(education.is_valid())
        self.assertFalse(certification.is_valid())
