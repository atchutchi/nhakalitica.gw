# Kalitica Networking Society Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir uma aplicação Django privada, trilingue e moderada para membros da Kalitica, funcionalmente derivada do CVLink e visualmente fiel aos quatro mockups aprovados.

**Architecture:** Importar a base Django estável do CVLink sem o seu conteúdo, dados ou identidade. Acrescentar um domínio `memberships` que controla candidatura, aprovação e acesso, mantendo adesão e publicação de perfil como processos separados. Aplicar o sistema visual Kalitica a páginas públicas, candidatura, rede privada e administração, com validação visual em desktop, tablet e mobile.

**Tech Stack:** Python 3.13, Django 5.2.16, Pillow, PostgreSQL em produção, SQLite em desenvolvimento, templates Django, CSS e JavaScript sem framework adicional, GitHub Actions.

## Global Constraints

- O repositório de destino é `atchutchi/nhakalitica.gw` na branch `main`.
- A base funcional vem de `C:\Users\binta\Documents\cvlink`, mas os projectos ficam independentes.
- O directório, os perfis, as áreas e as interacções exigem adesão aprovada.
- A confirmação de email permite login e candidatura, mas não abre a rede.
- Efectivo e Observador têm os mesmos direitos dentro da rede profissional.
- Adesão e publicação do perfil são decisões separadas.
- Não existem pagamentos, preços, quotas, dívidas, vagas ou planos comerciais no lançamento.
- Português, francês e inglês cobrem interface, validações e emails.
- `PRODUCT.md`, `DESIGN.md` e `output/mockups/*.png` são referências normativas.
- WCAG AA, foco visível, alvos de toque de 44px e funcionamento desde 320px são obrigatórios.
- Produção não recebe membros, métricas ou actividade fictícia.
- Cada tarefa termina com testes, revisão do diff, commit e push para `origin/main`.

## File Structure

- `config/`: configuração, URLs, internacionalização e segurança do projecto.
- `accounts/`: identidade, email, autenticação, conta e preferência de idioma.
- `memberships/`: candidatura, elegibilidade, estados, decisões e controlo de acesso.
- `profiles/`: perfil profissional, privacidade, revisão e publicação.
- `taxonomy/`: sectores, áreas, especializações e competências.
- `interactions/`: favoritos, comparação, contacto protegido, denúncias e notificações.
- `moderation/`: filas administrativas, decisões, suspensão e auditoria.
- `core/`: página pública, páginas institucionais, saúde e utilitários comuns.
- `templates/`: quatro famílias visuais correspondentes aos mockups aprovados.
- `static/css/`: tokens, base, páginas públicas, aplicação e administração.
- `static/js/`: navegação móvel, filtros, candidatura e interacções progressivas.
- `locale/`: catálogos `pt`, `fr` e `en`.
- `tests/`: configuração transversal, controlo de acesso, i18n e contrato visual.

---

### Task 1: Importar e neutralizar a base Django do CVLink

**Files:**
- Create from CVLink: `manage.py`, `requirements.txt`, `.env.example`, `.gitattributes`
- Create from CVLink: `config/`, `accounts/`, `profiles/`, `taxonomy/`, `interactions/`, `moderation/`, `core/`, `templates/`, `static/`, `tests/`, `.github/workflows/tests.yml`
- Modify: `README.md`
- Modify: `config/settings.py`
- Modify: `templates/base.html`
- Test: `tests/test_project_configuration.py`

**Interfaces:**
- Consumes: código no commit actual de `C:\Users\binta\Documents\cvlink`.
- Produces: projecto Django executável com `AUTH_USER_MODEL = "accounts.User"`, fuso horário `Africa/Bissau` e identidade Kalitica.

- [ ] **Step 1: Escrever o teste de configuração que falha**

```python
from django.conf import settings
from django.test import SimpleTestCase


class KaliticaConfigurationTests(SimpleTestCase):
    def test_project_identity_and_locale(self):
        self.assertEqual(settings.LANGUAGE_CODE, "pt")
        self.assertEqual(settings.TIME_ZONE, "Africa/Bissau")
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, "Kalitica <noreply@nhakalitica.gw>")
        self.assertIn("memberships", settings.INSTALLED_APPS)
```

- [ ] **Step 2: Executar o teste e confirmar a falha**

Run: `python manage.py test tests.test_project_configuration.KaliticaConfigurationTests -v 2`

Expected: FAIL porque o projecto e a aplicação `memberships` ainda não existem no destino.

- [ ] **Step 3: Copiar apenas o código versionado necessário do CVLink**

Copiar as pastas e ficheiros indicados em `Files`. Não copiar `.git`, `.venv`, `db.sqlite3`, `media`, `tmp`, `output`, `PRODUCT.md`, `DESIGN.md` ou os documentos de planeamento do CVLink.

- [ ] **Step 4: Neutralizar identidade e configuração**

Em `config/settings.py`, definir:

```python
LANGUAGE_CODE = "pt"
TIME_ZONE = "Africa/Bissau"
LANGUAGES = [
    ("pt", "Português"),
    ("fr", "Français"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "Kalitica <noreply@nhakalitica.gw>",
)
```

Acrescentar `memberships` a `INSTALLED_APPS`. Remover textos CVLink de metadados, emails e templates sem alterar ainda a lógica funcional.

- [ ] **Step 5: Executar verificações da base**

Run: `python manage.py makemigrations --check --dry-run`

Expected: nenhuma migração pendente nas aplicações importadas.

Run: `python manage.py check`

Expected: `System check identified no issues`.

Run: `python manage.py test`

Expected: suite importada passa depois das adaptações de identidade.

- [ ] **Step 6: Rever, fazer commit e push**

```powershell
git add manage.py requirements.txt .env.example .gitattributes .github config accounts profiles taxonomy interactions moderation core templates static tests README.md
git commit -m "feat: estabelecer base Django da Kalitica"
git push origin main
```

### Task 2: Criar o domínio de adesão e as regras de transição

**Files:**
- Create: `memberships/__init__.py`
- Create: `memberships/apps.py`
- Create: `memberships/models.py`
- Create: `memberships/services.py`
- Create: `memberships/admin.py`
- Create: `memberships/migrations/0001_initial.py`
- Create: `memberships/tests/test_models.py`
- Create: `memberships/tests/test_services.py`
- Modify: `accounts/models.py`

**Interfaces:**
- Consumes: `accounts.User`.
- Produces: `Membership`, `MembershipDecision`, `transition_membership(membership, actor, target_status, note)` e `Membership.can_access_network`.

- [ ] **Step 1: Escrever testes de modelo e transições**

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from memberships.models import Membership


class MembershipModelTests(TestCase):
    def test_approved_membership_opens_network_for_both_types(self):
        for member_type in [Membership.Type.EFFECTIVE, Membership.Type.OBSERVER]:
            user = get_user_model().objects.create_user(
                email=f"{member_type}@example.com",
                password="safe-password-123",
            )
            membership = Membership.objects.create(
                user=user,
                member_type=member_type,
                relationship=Membership.Relationship.CITIZEN,
                relationship_note="Cidadão da Guiné-Bissau.",
                status=Membership.Status.APPROVED,
            )
            self.assertTrue(membership.can_access_network)

    def test_suspended_membership_never_opens_network(self):
        membership = Membership(status=Membership.Status.SUSPENDED)
        self.assertFalse(membership.can_access_network)
```

```python
from django.core.exceptions import ValidationError
from django.test import TestCase
from memberships.services import transition_membership


class MembershipTransitionTests(TestCase):
    def test_refusal_requires_note(self):
        with self.assertRaisesMessage(ValidationError, "justificação"):
            transition_membership(
                self.membership,
                self.reviewer,
                "refused",
                "",
            )
```

- [ ] **Step 2: Confirmar as falhas**

Run: `python manage.py test memberships.tests -v 2`

Expected: FAIL porque `Membership` e `transition_membership` não existem.

- [ ] **Step 3: Implementar modelos com escolhas explícitas**

```python
class Membership(models.Model):
    class Type(models.TextChoices):
        EFFECTIVE = "effective", _("Efectivo")
        OBSERVER = "observer", _("Observador")

    class Relationship(models.TextChoices):
        CITIZEN = "citizen", _("Cidadão da Guiné-Bissau")
        DIASPORA = "diaspora", _("Descendente da diáspora")
        RELEVANT_LINK = "relevant_link", _("Ligação relevante")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Rascunho")
        SUBMITTED = "submitted", _("Submetida")
        UNDER_REVIEW = "under_review", _("Em análise")
        CORRECTIONS_REQUIRED = "corrections_required", _("Correcções necessárias")
        APPROVED = "approved", _("Aprovada")
        REFUSED = "refused", _("Recusada")
        SUSPENDED = "suspended", _("Suspensa")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    member_type = models.CharField(max_length=16, choices=Type.choices, blank=True)
    relationship = models.CharField(max_length=20, choices=Relationship.choices, blank=True)
    relationship_note = models.TextField(blank=True)
    motivation = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    @property
    def can_access_network(self):
        return self.status == self.Status.APPROVED
```

`MembershipDecision` guarda `membership`, `actor`, `from_status`, `to_status`, `note` e `created_at`.

- [ ] **Step 4: Implementar serviço transaccional**

```python
@transaction.atomic
def transition_membership(membership, actor, target_status, note):
    note = note.strip()
    if target_status in {
        Membership.Status.CORRECTIONS_REQUIRED,
        Membership.Status.REFUSED,
        Membership.Status.SUSPENDED,
    } and not note:
        raise ValidationError(_("Esta decisão exige uma justificação."))
    previous = membership.status
    membership.status = target_status
    membership.decided_at = timezone.now() if target_status in {
        Membership.Status.APPROVED,
        Membership.Status.REFUSED,
    } else membership.decided_at
    membership.save(update_fields=["status", "decided_at"])
    return MembershipDecision.objects.create(
        membership=membership,
        actor=actor,
        from_status=previous,
        to_status=target_status,
        note=note,
    )
```

- [ ] **Step 5: Criar migração e executar testes**

Run: `python manage.py makemigrations memberships`

Run: `python manage.py test memberships.tests -v 2`

Expected: PASS.

- [ ] **Step 6: Commit e push**

```powershell
git add memberships accounts/models.py
git commit -m "feat: adicionar dominio de adesao Kalitica"
git push origin main
```

### Task 3: Aplicar o controlo de acesso privado

**Files:**
- Create: `memberships/access.py`
- Create: `memberships/middleware.py`
- Create: `memberships/tests/test_access.py`
- Modify: `config/settings.py`
- Modify: `profiles/public_views.py`
- Modify: `taxonomy/views.py`
- Modify: `interactions/views.py`
- Modify: `accounts/views.py`

**Interfaces:**
- Consumes: `Membership.can_access_network`.
- Produces: `network_member_required(view_func)` e `membership_access_context(request)`.

- [ ] **Step 1: Escrever testes de isolamento**

```python
from django.test import TestCase
from django.urls import reverse


class PrivateNetworkAccessTests(TestCase):
    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse("search"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('search')}")

    def test_confirmed_candidate_is_sent_to_application(self):
        self.client.force_login(self.candidate)
        response = self.client.get(reverse("search"))
        self.assertRedirects(response, reverse("memberships:dashboard"))

    def test_approved_member_can_open_directory(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test memberships.tests.test_access -v 2`

Expected: FAIL porque as vistas importadas continuam públicas.

- [ ] **Step 3: Implementar o decorador**

```python
def network_member_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        membership = getattr(request.user, "membership", None)
        if not membership or not membership.can_access_network:
            messages.info(request, _("A rede fica disponível depois da aprovação."))
            return redirect("memberships:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapped
```

Aplicar o decorador a pesquisa, perfil de membro, fotografia, currículo, áreas, favoritos, comparação, contactos, denúncias e notificações. Não aplicar à página pública, registo, autenticação, candidatura ou saúde.

- [ ] **Step 4: Executar isolamento e regressão**

Run: `python manage.py test memberships profiles taxonomy interactions accounts -v 2`

Expected: PASS com expectativas públicas antigas actualizadas para rede privada.

- [ ] **Step 5: Commit e push**

```powershell
git add memberships config/settings.py profiles/public_views.py taxonomy/views.py interactions/views.py accounts/views.py
git commit -m "feat: restringir rede a membros aprovados"
git push origin main
```

### Task 4: Construir candidatura e acompanhamento de adesão

**Files:**
- Create: `memberships/forms.py`
- Create: `memberships/views.py`
- Create: `memberships/urls.py`
- Create: `memberships/tests/test_forms.py`
- Create: `memberships/tests/test_views.py`
- Create: `templates/memberships/dashboard.html`
- Create: `templates/memberships/application_form.html`
- Create: `templates/memberships/application_review.html`
- Modify: `config/urls.py`
- Create: `accounts/signals.py`

**Interfaces:**
- Consumes: `Membership`, `transition_membership` e perfil criado para cada utilizador.
- Produces: `membership_dashboard`, `membership_edit`, `membership_submit` e uma candidatura guardável em rascunho.

- [ ] **Step 1: Escrever testes de formulário e submissão**

```python
class MembershipApplicationTests(TestCase):
    def test_relevant_link_requires_explanation(self):
        form = MembershipApplicationForm(data={
            "member_type": "observer",
            "relationship": "relevant_link",
            "relationship_note": "",
            "motivation": "Quero colaborar com a rede.",
        }, instance=self.membership)
        self.assertFalse(form.is_valid())
        self.assertIn("relationship_note", form.errors)

    def test_submission_locks_application_until_corrections(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("memberships:submit"))
        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, "submitted")
        self.assertIsNotNone(self.membership.submitted_at)
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test memberships.tests.test_forms memberships.tests.test_views -v 2`

Expected: FAIL porque formulários e URLs não existem.

- [ ] **Step 3: Implementar validação e submissão**

```python
def clean(self):
    cleaned = super().clean()
    if (
        cleaned.get("relationship") == Membership.Relationship.RELEVANT_LINK
        and not cleaned.get("relationship_note", "").strip()
    ):
        self.add_error(
            "relationship_note",
            _("Explica a tua ligação relevante à Guiné-Bissau."),
        )
    return cleaned
```

A edição é permitida em `draft` e `corrections_required`. A submissão exige email confirmado, tipo, relação, justificação quando aplicável, motivação, consentimentos e campos profissionais mínimos.

- [ ] **Step 4: Ligar criação automática e URLs**

Criar `Membership` e `Profile` quando uma conta é criada. Adicionar `path("adesao/", include("memberships.urls"))`.

- [ ] **Step 5: Executar testes**

Run: `python manage.py test memberships accounts profiles -v 2`

Expected: PASS.

- [ ] **Step 6: Commit e push**

```powershell
git add memberships templates/memberships config/urls.py accounts/signals.py
git commit -m "feat: criar candidatura de membro"
git push origin main
```

### Task 5: Separar publicação profissional da adesão

**Files:**
- Modify: `profiles/models.py`
- Modify: `profiles/views.py`
- Modify: `profiles/selectors.py`
- Modify: `profiles/forms.py`
- Create: `profiles/migrations/0011_kalitica_membership_visibility.py`
- Modify: `profiles/tests/test_profile_completion.py`
- Modify: `profiles/tests/test_search.py`
- Create: `profiles/tests/test_membership_visibility.py`

**Interfaces:**
- Consumes: `user.membership.can_access_network`.
- Produces: `Profile.is_visible_to(viewer)`, `member_profiles(viewer, params)` e estados de publicação independentes.

- [ ] **Step 1: Escrever testes de visibilidade**

```python
class MembershipProfileVisibilityTests(TestCase):
    def test_approved_membership_does_not_publish_incomplete_profile(self):
        self.profile.review_status = Profile.ReviewStatus.DRAFT
        self.profile.save()
        self.assertFalse(self.profile.is_visible_to(self.other_member))

    def test_member_can_hide_an_approved_profile(self):
        self.profile.is_discoverable = False
        self.profile.review_status = Profile.ReviewStatus.APPROVED
        self.profile.save()
        self.assertFalse(self.profile.is_visible_to(self.other_member))

    def test_suspension_hides_profile_without_deleting_it(self):
        self.profile.user.membership.status = Membership.Status.SUSPENDED
        self.profile.user.membership.save()
        self.assertFalse(self.profile.is_visible_to(self.other_member))
        self.assertTrue(Profile.objects.filter(pk=self.profile.pk).exists())
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test profiles.tests.test_membership_visibility -v 2`

Expected: FAIL porque a visibilidade ainda depende apenas da revisão de perfil.

- [ ] **Step 3: Implementar contrato de visibilidade**

```python
def is_visible_to(self, viewer):
    viewer_membership = getattr(viewer, "membership", None)
    owner_membership = getattr(self.user, "membership", None)
    return bool(
        viewer.is_authenticated
        and viewer_membership
        and viewer_membership.can_access_network
        and owner_membership
        and owner_membership.can_access_network
        and self.review_status == self.ReviewStatus.APPROVED
        and self.is_discoverable
    )
```

Renomear o selector público para `member_profiles` e filtrar adesões aprovadas, publicação aprovada e `is_discoverable=True` antes de aplicar a pesquisa.

- [ ] **Step 4: Preservar privacidade por campo**

Garantir que localização, email, telefone e currículo usam escolhas separadas. O download de currículo chama `is_visible_to(request.user)` e valida `cv_visibility` antes de devolver o ficheiro.

- [ ] **Step 5: Executar testes de perfil e pesquisa**

Run: `python manage.py test profiles -v 2`

Expected: PASS.

- [ ] **Step 6: Commit e push**

```powershell
git add profiles
git commit -m "feat: separar adesao e publicacao profissional"
git push origin main
```

### Task 6: Adaptar interacções à rede privada

**Files:**
- Modify: `interactions/models.py`
- Modify: `interactions/services.py`
- Modify: `interactions/views.py`
- Modify: `interactions/tests/test_services.py`
- Modify: `interactions/tests/test_views.py`
- Create: `interactions/tests/test_privacy.py`

**Interfaces:**
- Consumes: `Profile.is_visible_to(viewer)` e `network_member_required`.
- Produces: favoritos, comparação, contacto e notificações que nunca ultrapassam a privacidade do perfil.

- [ ] **Step 1: Escrever testes de privacidade das interacções**

```python
class InteractionPrivacyTests(TestCase):
    def test_candidate_cannot_favorite_profile(self):
        self.client.force_login(self.candidate)
        response = self.client.post(reverse("interactions:favorite-add", args=[self.profile.slug]))
        self.assertRedirects(response, reverse("memberships:dashboard"))
        self.assertFalse(Favorite.objects.exists())

    def test_contact_request_does_not_expose_email_before_acceptance(self):
        contact = create_contact(self.sender, self.profile, "Colaboração", "Olá")
        self.assertNotIn(self.profile.user.email, contact.message)
        self.assertEqual(contact.status, ContactRequest.Status.PENDING)
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test interactions.tests.test_privacy -v 2`

Expected: FAIL com o comportamento público herdado.

- [ ] **Step 3: Aplicar validação central**

```python
def ensure_member_profile_action(user, profile):
    if not profile.is_visible_to(user):
        raise PermissionDenied(_("Este perfil não está disponível."))
```

Usar a função em favorito, gosto, contacto, denúncia, comparação e exportação. Não incluir telefone ou email na mensagem de contacto. A partilha posterior depende de aceitação e preferências.

- [ ] **Step 4: Executar testes**

Run: `python manage.py test interactions -v 2`

Expected: PASS.

- [ ] **Step 5: Commit e push**

```powershell
git add interactions
git commit -m "feat: proteger interacoes entre membros"
git push origin main
```

### Task 7: Criar revisão administrativa de adesão e suspensão

**Files:**
- Modify: `moderation/views.py`
- Modify: `moderation/urls.py`
- Modify: `moderation/services.py`
- Modify: `moderation/models.py`
- Create: `moderation/tests/test_memberships.py`
- Create: `templates/moderation/membership_list.html`
- Create: `templates/moderation/membership_review.html`
- Modify: `templates/moderation/dashboard.html`
- Create: `moderation/migrations/0002_membership_audit.py`

**Interfaces:**
- Consumes: `transition_membership` e `MembershipDecision`.
- Produces: filas de adesão, decisões confirmadas, suspensão, reactivação e auditoria não editável.

- [ ] **Step 1: Escrever testes de permissões e auditoria**

```python
class MembershipModerationTests(TestCase):
    def test_non_staff_cannot_review_membership(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("moderation:membership-review", args=[self.application.pk]))
        self.assertEqual(response.status_code, 403)

    def test_approval_records_actor_and_transition(self):
        self.client.force_login(self.reviewer)
        response = self.client.post(
            reverse("moderation:membership-review", args=[self.application.pk]),
            {"action": "approved", "note": "Ligação confirmada."},
        )
        self.assertRedirects(response, reverse("moderation:membership-list"))
        decision = MembershipDecision.objects.get(membership=self.application)
        self.assertEqual(decision.actor, self.reviewer)
        self.assertEqual(decision.to_status, "approved")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test moderation.tests.test_memberships -v 2`

Expected: FAIL porque as rotas administrativas ainda não existem.

- [ ] **Step 3: Implementar filas e decisão**

As acções permitidas são `under_review`, `corrections_required`, `approved`, `refused`, `suspended` e regresso de suspensão para `approved`. Usar POST, CSRF, transacção e mensagem de confirmação.

- [ ] **Step 4: Integrar auditoria**

Criar uma entrada `AuditLog` para cada decisão com `actor`, `action`, `target_model`, `target_id`, `details` e `created_at`. Não disponibilizar edição ou eliminação na interface.

- [ ] **Step 5: Executar testes administrativos**

Run: `python manage.py test moderation memberships -v 2`

Expected: PASS.

- [ ] **Step 6: Commit e push**

```powershell
git add moderation templates/moderation
git commit -m "feat: moderar candidaturas e suspensoes"
git push origin main
```

### Task 8: Implementar páginas públicas e autenticação fiéis ao painel 01

**Files:**
- Modify: `templates/base.html`
- Modify: `templates/core/home.html`
- Create: `templates/core/about.html`
- Create: `templates/core/membership_types.html`
- Create: `templates/core/how_it_works.html`
- Modify: `templates/registration/*.html`
- Create: `static/css/tokens.css`
- Create: `static/css/public.css`
- Create: `static/css/auth.css`
- Create: `static/js/navigation.js`
- Create: `static/img/kalitica-logo.png`
- Modify: `core/views.py`
- Modify: `core/urls.py`
- Modify: `core/tests.py`

**Interfaces:**
- Consumes: design tokens de `DESIGN.md` e logótipo oficial local.
- Produces: página pública, institucional e autenticação com navegação PT FR EN.

- [ ] **Step 1: Escrever testes de contrato visual e conteúdo**

```python
class PublicVisualContractTests(TestCase):
    def test_home_uses_kalitica_public_shell(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "A rede profissional da Guiné-Bissau")
        self.assertContains(response, 'class="public-header"')
        self.assertContains(response, 'class="hero-network"')
        self.assertContains(response, reverse("memberships:dashboard"))
        self.assertNotContains(response, "CVLink")
        self.assertNotContains(response, "10€/mês")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test core.tests.PublicVisualContractTests -v 2`

Expected: FAIL com os templates importados.

- [ ] **Step 3: Criar tokens CSS exactos**

```css
:root {
  --color-primary: #2b7a77;
  --color-primary-deep: #1e5a57;
  --color-navy: #0b3d61;
  --color-mint: #5ab59f;
  --color-turquoise: #22b8c7;
  --color-surface: #ffffff;
  --color-surface-soft: #f6faf9;
  --color-ink: #0a1720;
  --color-muted: #536763;
  --color-border: #d7e5e1;
  --radius-control: 6px;
  --radius-panel: 10px;
  --space-1: 4px;
  --space-2: 8px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
}
```

- [ ] **Step 4: Implementar composição do painel 01**

Reproduzir cabeçalho, hero, cartões de elegibilidade, tipos de adesão, formulários de autenticação com painel azul e versão mobile. Usar conteúdo real aprovado e o logótipo oficial. Não rasterizar texto da interface.

- [ ] **Step 5: Executar testes e Impeccable detector**

Run: `python manage.py test core accounts -v 2`

Run: `node C:\Users\binta\.codex\skills\impeccable\scripts\detect.mjs --json templates static/css`

Expected: testes passam e não existem violações de contraste, overflow, gradiente de texto, glassmorphism ou raios excessivos.

- [ ] **Step 6: Inspeccionar 1440px, 768px e 375px**

Comparar screenshots com `output/mockups/01-paginas-publicas-e-autenticacao.png`. Corrigir composição, densidade, tipografia, navegação e empilhamento antes do commit.

- [ ] **Step 7: Commit e push**

```powershell
git add templates/base.html templates/core templates/registration static core
git commit -m "feat: criar experiencia publica Kalitica"
git push origin main
```

### Task 9: Implementar candidatura fiel ao painel 02

**Files:**
- Modify: `templates/memberships/dashboard.html`
- Modify: `templates/memberships/application_form.html`
- Modify: `templates/memberships/application_review.html`
- Create: `templates/memberships/_progress.html`
- Create: `static/css/onboarding.css`
- Create: `static/js/onboarding.js`
- Modify: `memberships/tests/test_views.py`

**Interfaces:**
- Consumes: vistas da Task 4 e tokens da Task 8.
- Produces: painel de candidatura, passos, estados e controlos de privacidade do painel 02.

- [ ] **Step 1: Escrever teste de estrutura e estado**

```python
def test_candidate_dashboard_shows_real_progress_and_lock(self):
    self.client.force_login(self.candidate)
    response = self.client.get(reverse("memberships:dashboard"))
    self.assertContains(response, 'class="application-progress"')
    self.assertContains(response, "A minha candidatura")
    self.assertContains(response, "Revisão manual")
    self.assertNotContains(response, "Directório")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test memberships.tests.test_views -v 2`

Expected: FAIL até a estrutura visual ser implementada.

- [ ] **Step 3: Construir os estados do painel 02**

Criar navegação lateral, progresso real, cartões de tipo de adesão, relação com a Guiné-Bissau, editor profissional, linha temporal, correcções e aprovação. O template decide o estado a partir de `membership.status`, nunca de texto estático.

- [ ] **Step 4: Testar e inspeccionar**

Run: `python manage.py test memberships profiles -v 2`

Inspeccionar 1366px e 375px contra `output/mockups/02-adesao-e-aprovacao.png`.

- [ ] **Step 5: Commit e push**

```powershell
git add templates/memberships static/css/onboarding.css static/js/onboarding.js memberships/tests
git commit -m "feat: desenhar fluxo de adesao Kalitica"
git push origin main
```

### Task 10: Implementar rede privada fiel ao painel 03

**Files:**
- Modify: `templates/accounts/dashboard.html`
- Modify: `templates/profiles/search.html`
- Modify: `templates/profiles/_profile_card.html`
- Modify: `templates/profiles/public_detail.html`
- Modify: `templates/taxonomy/area_list.html`
- Modify: `templates/taxonomy/area_detail.html`
- Modify: `templates/interactions/favorites.html`
- Modify: `templates/interactions/compare.html`
- Modify: `templates/interactions/contact_form.html`
- Modify: `templates/interactions/notifications.html`
- Create: `static/css/app-shell.css`
- Create: `static/css/directory.css`
- Create: `static/js/directory.js`
- Modify: `profiles/tests/test_search.py`
- Modify: `interactions/tests/test_views.py`

**Interfaces:**
- Consumes: acesso, selecção, perfis e interacções das Tasks 3, 5 e 6.
- Produces: painel do membro, directório, perfil, áreas, favoritos, comparação, contacto e notificações do painel 03.

- [ ] **Step 1: Escrever testes de contrato da rede**

```python
def test_directory_uses_private_network_shell(self):
    self.client.force_login(self.member)
    response = self.client.get(reverse("search"))
    self.assertContains(response, 'class="member-shell"')
    self.assertContains(response, 'class="directory-filters"')
    self.assertContains(response, "Pesquisar profissionais")
    self.assertContains(response, "Relação com a Guiné-Bissau")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test profiles.tests.test_search interactions.tests.test_views -v 2`

Expected: FAIL até os templates novos existirem.

- [ ] **Step 3: Implementar a composição do painel 03**

Usar navegação superior compacta, filtro lateral estável, resultados em linhas, perfil em secções, índice de áreas, lista privada, tabela de comparação, pedido de contacto e notificações. Em mobile, filtros abrem num painel acessível e a lista continua legível sem deslocamento horizontal.

- [ ] **Step 4: Testar dados longos, vazio e erro**

Criar fixtures de teste com nomes longos, competências extensas, zero resultados, currículo oculto e pedido de contacto inválido. Confirmar que cada estado preserva hierarquia e explica a próxima acção.

- [ ] **Step 5: Executar e inspeccionar**

Run: `python manage.py test profiles taxonomy interactions accounts -v 2`

Inspeccionar 1440px, 1024px, 768px e 375px contra `output/mockups/03-rede-profissional-privada.png`.

- [ ] **Step 6: Commit e push**

```powershell
git add templates/accounts templates/profiles templates/taxonomy templates/interactions static/css/app-shell.css static/css/directory.css static/js/directory.js profiles/tests interactions/tests
git commit -m "feat: criar rede profissional privada"
git push origin main
```

### Task 11: Implementar conta e administração fiéis ao painel 04

**Files:**
- Modify: `templates/accounts/edit.html`
- Modify: `templates/accounts/deactivate.html`
- Modify: `templates/profiles/edit.html`
- Modify: `templates/profiles/section_form.html`
- Modify: `templates/moderation/*.html`
- Create: `static/css/settings.css`
- Create: `static/css/admin.css`
- Create: `static/js/admin-actions.js`
- Modify: `accounts/tests/test_account_security.py`
- Modify: `moderation/tests/test_views.py`
- Modify: `moderation/tests/test_memberships.py`

**Interfaces:**
- Consumes: conta, privacidade, moderação e auditoria implementadas.
- Produces: definições do membro e administração do painel 04.

- [ ] **Step 1: Escrever testes de estrutura e confirmação destrutiva**

```python
def test_suspension_requires_confirmation_and_reason(self):
    self.client.force_login(self.reviewer)
    response = self.client.post(
        reverse("moderation:membership-review", args=[self.application.pk]),
        {"action": "suspended", "note": ""},
    )
    self.assertEqual(response.status_code, 200)
    self.assertFormError(response.context["form"], "note", "Esta decisão exige uma justificação.")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test accounts.tests.test_account_security moderation -v 2`

Expected: FAIL até validação e templates finais estarem ligados.

- [ ] **Step 3: Implementar composição do painel 04**

Criar definições, editor modular, privacidade, alteração de palavra-passe, desactivação, painel administrativo, revisão de adesão, revisão de perfil e auditoria. Usar navegação azul escura apenas no administrador. Acções destrutivas exigem confirmação clara e não dependem apenas da cor.

- [ ] **Step 4: Executar e inspeccionar**

Run: `python manage.py test accounts moderation profiles -v 2`

Inspeccionar desktop e tablet contra `output/mockups/04-conta-privacidade-e-administracao.png`.

- [ ] **Step 5: Commit e push**

```powershell
git add templates/accounts templates/profiles templates/moderation static/css/settings.css static/css/admin.css static/js/admin-actions.js accounts/tests moderation/tests
git commit -m "feat: finalizar conta e administracao Kalitica"
git push origin main
```

### Task 12: Completar traduções, acessibilidade e verificação de produção

**Files:**
- Create: `locale/pt/LC_MESSAGES/django.po`
- Create: `locale/fr/LC_MESSAGES/django.po`
- Create: `locale/en/LC_MESSAGES/django.po`
- Modify: Python e templates com mensagens ainda não marcadas para tradução
- Create: `tests/test_i18n.py`
- Create: `tests/test_visual_contract.py`
- Modify: `.github/workflows/tests.yml`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `design-qa.md`

**Interfaces:**
- Consumes: aplicação completa.
- Produces: três idiomas, QA documentado, CI e configuração de produção verificável.

- [ ] **Step 1: Escrever testes de idioma e codificação**

```python
from django.test import TestCase, override_settings
from django.urls import reverse


class InternationalizationTests(TestCase):
    @override_settings(LANGUAGE_CODE="fr")
    def test_french_home_has_translated_primary_action(self):
        response = self.client.get(reverse("home"), HTTP_ACCEPT_LANGUAGE="fr")
        self.assertContains(response, "Demander l’adhésion")

    @override_settings(LANGUAGE_CODE="en")
    def test_english_login_has_no_encoding_artifacts(self):
        response = self.client.get(reverse("accounts:login"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertContains(response, "Sign in")
        self.assertNotContains(response, "Ã")
```

- [ ] **Step 2: Confirmar a falha**

Run: `python manage.py test tests.test_i18n -v 2`

Expected: FAIL antes de os catálogos estarem completos.

- [ ] **Step 3: Extrair, traduzir e compilar mensagens**

Run: `python manage.py makemessages -l pt -l fr -l en --no-obsolete`

Preencher traduções humanas para navegação, formulários, validação, estados e emails. Não traduzir biografias, experiência ou outro conteúdo criado pelos membros.

Run: `python manage.py compilemessages`

Expected: três catálogos compilados sem erros.

- [ ] **Step 4: Executar suite e verificações Django**

Run: `python manage.py makemigrations --check --dry-run`

Run: `python manage.py check`

Run: `python manage.py test`

Expected: todas as verificações passam.

- [ ] **Step 5: Executar verificação de produção**

```powershell
$env:DEBUG='False'
$env:SECRET_KEY='test-only-long-production-check-key'
$env:ALLOWED_HOSTS='nhakalitica.gw,www.nhakalitica.gw'
$env:CSRF_TRUSTED_ORIGINS='https://nhakalitica.gw,https://www.nhakalitica.gw'
python manage.py check --deploy
```

Expected: nenhuma falha de segurança. Avisos que dependam do servidor de produção devem ser documentados e resolvidos na configuração de deployment.

- [ ] **Step 6: Fazer auditoria Impeccable e revisão visual final**

Run: `node C:\Users\binta\.codex\skills\impeccable\scripts\detect.mjs --json templates static/css static/js`

Verificar teclado, foco, movimento reduzido, contraste, zoom a 200 por cento, textos longos nos três idiomas e screenshots a 1440px, 1024px, 768px, 375px e 320px. Ler cada screenshot e comparar com o painel correspondente.

- [ ] **Step 7: Actualizar CI e documentação**

GitHub Actions deve instalar dependências, validar migrações, executar `check`, correr todos os testes e rejeitar artefactos de codificação com `rg "Ã.|Â." templates locale -g "*.html" -g "*.po"`.

- [ ] **Step 8: Commit e push final**

```powershell
git add locale tests .github README.md .env.example design-qa.md
git commit -m "test: validar idiomas acessibilidade e producao"
git push origin main
```

- [ ] **Step 9: Confirmar estado final do repositório**

Run: `git status --short --branch`

Expected: `## main...origin/main` sem ficheiros modificados ou não rastreados.
