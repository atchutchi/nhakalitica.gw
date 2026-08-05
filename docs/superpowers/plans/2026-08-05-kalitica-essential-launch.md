# Kalitica Essential Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Concluir o primeiro lançamento de `nhakalitica.gw` com interface e documentos em três idiomas, consentimentos auditáveis, representação privada de organizações, emails operacionais em português e eliminação de contas após 30 dias.

**Architecture:** A implementação mantém a aplicação Django monolítica e separa responsabilidades em serviços pequenos. `core` publica conteúdo legal, `accounts` regista consentimentos e ciclo de eliminação, `memberships` guarda a representação de organizações, `profiles` controla a publicação opcional e `core.emailing` centraliza o envio operacional. As mudanças são entregues por migrações compatíveis e activadas progressivamente através dos fluxos existentes.

**Tech Stack:** Python 3.12+, Django 5.2.16, templates Django, gettext, SQLite em desenvolvimento, PostgreSQL em produção, unittest do Django e GitHub Actions.

## Global Constraints

- O domínio oficial é `nhakalitica.gw`.
- A entidade responsável provisória é Kalitica Networking Society.
- O contacto oficial é `info@nhakalitica.gw`.
- Interface e documentos legais em português, francês e inglês.
- Emails automáticos apenas em português.
- Uma organização nunca acede sem um representante pessoal aprovado.
- Dados da organização são privados por defeito e só são publicados mediante consentimento explícito.
- Desactivação imediata, recuperação durante 30 dias e eliminação posterior dos dados pessoais.
- Sem pagamentos, vagas, equipas empresariais ou facturação neste lançamento.
- Implementação sempre com ciclo TDD: teste vermelho, implementação mínima, teste verde e refactorização.
- Cada tarefa termina com commit e push para `main`, conforme o processo do projecto.

---

### Task 1: Identidade oficial e páginas legais trilingues

**Files:**
- Modify: `config/settings.py`
- Modify: `.env.example`
- Modify: `core/urls.py`
- Modify: `core/views.py`
- Modify: `core/sitemaps.py`
- Modify: `templates/core/_public_footer.html`
- Modify: `templates/core/_public_header.html`
- Modify: `templates/registration/signup.html`
- Create: `templates/core/terms.html`
- Create: `templates/core/privacy.html`
- Create: `templates/core/code_of_conduct.html`
- Modify: `core/tests.py`
- Modify: `locale/en/LC_MESSAGES/django.po`
- Modify: `locale/fr/LC_MESSAGES/django.po`
- Modify: `locale/en/LC_MESSAGES/django.mo`
- Modify: `locale/fr/LC_MESSAGES/django.mo`
- Modify: `README.md`
- Create: `requirements-dev.txt`

**Interfaces:**
- Produces: settings `PUBLIC_BASE_URL`, `KALITICA_CONTACT_EMAIL`, `LEGAL_DOCUMENT_VERSION`, `LEGAL_EFFECTIVE_DATE`.
- Produces: named URLs `terms`, `privacy`, `code-of-conduct`.
- Consumes: existing public layout and locale middleware.

- [ ] **Step 1: Escrever testes vermelhos para configuração e rotas legais**

Adicionar a `core/tests.py` testes que exijam as três rotas, versão, contacto, canonical e idioma:

```python
class LegalPageTests(TestCase):
    def test_legal_pages_are_public_and_versioned(self):
        expected = {
            "/termos/": "Termos de Utilização",
            "/privacidade/": "Política de Privacidade",
            "/codigo-de-conduta/": "Código de Conduta",
        }
        for path, heading in expected.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, heading)
                self.assertContains(response, "Versão 1.0")
                self.assertContains(response, "info@nhakalitica.gw")
                self.assertContains(response, 'rel="canonical"')

    def test_legal_pages_are_available_in_english_and_french(self):
        self.client.post("/i18n/setlang/", {"language": "en", "next": "/privacidade/"})
        self.assertContains(self.client.get("/privacidade/"), "Privacy Policy")
        self.client.post("/i18n/setlang/", {"language": "fr", "next": "/privacidade/"})
        self.assertContains(self.client.get("/privacidade/"), "Politique de confidentialité")
```

- [ ] **Step 2: Executar os testes e confirmar falha por rotas inexistentes**

Run: `.\.venv\Scripts\python.exe manage.py test core.tests.LegalPageTests --verbosity 2`

Expected: FAIL com respostas 404 ou classe inexistente.

- [ ] **Step 3: Implementar configuração e views legais mínimas**

Adicionar a `config/settings.py`:

```python
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
KALITICA_CONTACT_EMAIL = os.getenv("KALITICA_CONTACT_EMAIL", "info@nhakalitica.gw")
LEGAL_DOCUMENT_VERSION = "1.0"
LEGAL_EFFECTIVE_DATE = "2026-08-05"
```

Criar em `core/views.py` uma função comum:

```python
def legal_page(request, template_name, route_name):
    return render(request, template_name, {
        "legal_version": settings.LEGAL_DOCUMENT_VERSION,
        "legal_effective_date": settings.LEGAL_EFFECTIVE_DATE,
        "contact_email": settings.KALITICA_CONTACT_EMAIL,
        "canonical_url": request.build_absolute_uri(reverse(route_name)),
    })
```

As três views finas chamam esta função e as rotas usam os caminhos portugueses aprovados.

- [ ] **Step 4: Criar conteúdo legal completo nas três línguas**

Cada template deve usar blocos traduzíveis e conter as secções exactas da especificação. Antes de redigir, consultar fontes jurídicas primárias aplicáveis e registar no rodapé que o conteúdo requer revisão jurídica final antes do lançamento. Não copiar textos de terceiros.

Os Termos incluem: elegibilidade, aprovação, conta, exactidão, conduta, moderação, suspensão, conteúdo, ausência de cobrança e alterações.

A Política inclui: responsável, dados, finalidades, visibilidade, contactos, currículos, conservação, segurança, direitos, transferências e contacto.

O Código inclui: respeito, fraude, falsidade, discriminação, assédio, spam, recolha de dados, denúncia e consequências.

- [ ] **Step 5: Ligar os documentos no cabeçalho, rodapé e registo**

Substituir todos os contactos públicos por `mailto:info@nhakalitica.gw`. O rodapé deve ligar às três páginas. O rótulo de aceitação no registo deve conter ligações clicáveis para Termos e Privacidade sem alterar a obrigatoriedade do checkbox.

- [ ] **Step 6: Actualizar catálogos e compilar traduções**

Adicionar `polib>=1.2,<2` a `requirements-dev.txt` e instalar com:

Run: `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`

Run: `.\.venv\Scripts\python.exe manage.py makemessages -l en -l fr`

Preencher todas as entradas novas e executar:

Compilar os catálogos com `polib` para evitar dependência do GNU gettext no Windows:

Run: `.\.venv\Scripts\python.exe -c "import polib; [polib.pofile(path).save_as_mofile(path.replace('.po', '.mo')) for path in ('locale/en/LC_MESSAGES/django.po', 'locale/fr/LC_MESSAGES/django.po')]"`

- [ ] **Step 7: Executar testes verdes e verificação da tarefa**

Run: `.\.venv\Scripts\python.exe manage.py test core.tests.LegalPageTests core.tests.InterfaceLanguageTests --verbosity 2`

Expected: PASS.

Run: `git diff --check`

Expected: sem erros.

- [ ] **Step 8: Commit e push**

```powershell
git add config/settings.py .env.example core templates/core templates/registration/signup.html locale README.md requirements-dev.txt
git commit -m "feat: adicionar documentos legais trilingues"
git push origin main
```

---

### Task 2: Consentimentos legais auditáveis

**Files:**
- Create: `accounts/migrations/0003_legal_acceptance.py`
- Modify: `accounts/models.py`
- Create: `accounts/legal.py`
- Modify: `accounts/views.py`
- Modify: `memberships/views.py`
- Modify: `profiles/views.py`
- Modify: `accounts/admin.py`
- Create: `accounts/tests/test_legal_acceptance.py`
- Modify: `accounts/tests/test_auth.py`
- Modify: `memberships/tests/test_views.py`
- Modify: `profiles/tests/test_views.py`

**Interfaces:**
- Produces: `LegalAcceptance` and `record_legal_acceptance(user, document_type, source) -> LegalAcceptance`.
- Consumes: `settings.LEGAL_DOCUMENT_VERSION` from Task 1.

- [ ] **Step 1: Escrever testes vermelhos para o registo de aceitação**

```python
class LegalAcceptanceTests(TestCase):
    def test_signup_records_terms_and_privacy_once(self):
        response = self.client.post("/conta/criar/", self.valid_signup_data())
        user = get_user_model().objects.get(email="legal@example.com")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LegalAcceptance.objects.filter(
            user=user, document_type="terms", version="1.0", source="signup"
        ).exists())
        self.assertTrue(LegalAcceptance.objects.filter(
            user=user, document_type="privacy", version="1.0", source="signup"
        ).exists())

    def test_recording_same_acceptance_is_idempotent(self):
        first = record_legal_acceptance(self.user, "privacy", "membership")
        second = record_legal_acceptance(self.user, "privacy", "membership")
        self.assertEqual(first.pk, second.pk)
```

- [ ] **Step 2: Executar e confirmar falha por modelo inexistente**

Run: `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_legal_acceptance --verbosity 2`

Expected: ERROR ou FAIL porque `LegalAcceptance` ainda não existe.

- [ ] **Step 3: Implementar modelo e migração**

```python
class LegalAcceptance(models.Model):
    class DocumentType(models.TextChoices):
        TERMS = "terms", _("Termos de Utilização")
        PRIVACY = "privacy", _("Política de Privacidade")
        CODE = "code", _("Código de Conduta")

    class Source(models.TextChoices):
        SIGNUP = "signup", _("Registo")
        MEMBERSHIP = "membership", _("Candidatura")
        PROFILE = "profile", _("Publicação do perfil")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="legal_acceptances", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=16, choices=DocumentType.choices)
    version = models.CharField(max_length=30)
    source = models.CharField(max_length=16, choices=Source.choices)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=("user", "document_type", "version", "source"),
            name="unique_legal_acceptance",
        )]
```

- [ ] **Step 4: Implementar serviço idempotente**

```python
def record_legal_acceptance(user, document_type, source):
    acceptance, _created = LegalAcceptance.objects.get_or_create(
        user=user,
        document_type=document_type,
        version=settings.LEGAL_DOCUMENT_VERSION,
        source=source,
    )
    return acceptance
```

- [ ] **Step 5: Integrar nos três fluxos**

Após criação da conta, registar Termos e Privacidade com origem `signup`. Após transição bem-sucedida da candidatura para `submitted`, registar Privacidade e Código com origem `membership`. Após submissão válida do perfil, registar Termos e Privacidade com origem `profile` e manter os campos históricos do perfil.

- [ ] **Step 6: Executar testes focados e migrações**

Run: `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`

Expected: `No changes detected` depois de a migração ser criada.

Run: `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_legal_acceptance accounts.tests.test_auth memberships.tests.test_views profiles.tests.test_views --verbosity 2`

Expected: PASS.

- [ ] **Step 7: Commit e push**

```powershell
git add accounts memberships/views.py profiles/views.py
git commit -m "feat: registar consentimentos legais"
git push origin main
```

---

### Task 3: Representação privada de organizações

**Files:**
- Modify: `memberships/models.py`
- Create: `memberships/migrations/0003_organization_representation.py`
- Modify: `memberships/forms.py`
- Modify: `memberships/views.py`
- Modify: `memberships/admin.py`
- Modify: `templates/memberships/application_form.html`
- Modify: `templates/memberships/application_review.html`
- Modify: `templates/moderation/membership_review.html`
- Modify: `profiles/models.py`
- Create: `profiles/migrations/0013_profile_show_organization_on_profile.py`
- Modify: `profiles/forms.py`
- Modify: `templates/profiles/edit.html`
- Modify: `templates/profiles/public_detail.html`
- Modify: `memberships/tests/test_forms.py`
- Modify: `memberships/tests/test_views.py`
- Modify: `profiles/tests/test_models.py`
- Modify: `profiles/tests/test_membership_visibility.py`

**Interfaces:**
- Produces: private membership fields `represents_organization`, `organization_name`, `organization_role`, `organization_purpose`.
- Produces: profile consent `show_organization_on_profile`.
- Produces: public snapshot keys `organization_name`, `organization_role` only when authorised.

- [ ] **Step 1: Escrever testes vermelhos de validação e privacidade**

```python
def test_organization_fields_are_required_for_representative(self):
    form = MembershipApplicationForm(data=self.application_data(
        represents_organization=True,
        organization_name="",
        organization_role="",
        organization_purpose="",
    ))
    self.assertFalse(form.is_valid())
    self.assertIn("organization_name", form.errors)
    self.assertIn("organization_role", form.errors)
    self.assertIn("organization_purpose", form.errors)

def test_private_organization_data_is_not_in_public_snapshot_without_consent(self):
    self.membership.represents_organization = True
    self.membership.organization_name = "Organização Teste"
    self.membership.organization_role = "Representante"
    self.membership.save()
    payload = self.profile.build_public_snapshot()
    self.assertNotIn("organization_name", payload)
    self.assertNotIn("organization_role", payload)

def test_disabling_representation_clears_publication_consent(self):
    self.profile.show_organization_on_profile = True
    self.profile.save(update_fields=("show_organization_on_profile",))
    form = MembershipApplicationForm(data=self.application_data(represents_organization=False), instance=self.membership)
    self.assertTrue(form.is_valid())
    form.save()
    self.profile.refresh_from_db()
    self.assertFalse(self.profile.show_organization_on_profile)
```

- [ ] **Step 2: Executar e confirmar falhas pelos campos inexistentes**

Run: `.\.venv\Scripts\python.exe manage.py test memberships.tests.test_forms profiles.tests.test_models --verbosity 2`

Expected: FAIL ou ERROR nos novos testes.

- [ ] **Step 3: Implementar campos e migrações**

Adicionar ao `Membership` quatro campos com valores vazios por defeito. Adicionar ao `Profile`:

```python
show_organization_on_profile = models.BooleanField(
    _("mostrar organização no perfil"), default=False
)
```

- [ ] **Step 4: Implementar limpeza e validação do formulário**

```python
if cleaned.get("represents_organization"):
    for field_name in ("organization_name", "organization_role", "organization_purpose"):
        if not cleaned.get(field_name, "").strip():
            self.add_error(field_name, _("Este campo é obrigatório para representantes de organizações."))
else:
    cleaned["organization_name"] = ""
    cleaned["organization_role"] = ""
    cleaned["organization_purpose"] = ""
```

- [ ] **Step 5: Implementar publicação opcional no snapshot**

`build_public_snapshot()` deve acrescentar nome e cargo apenas quando `show_organization_on_profile` está activo, a adesão está aprovada e `represents_organization` está activo. `organization_purpose` nunca entra no snapshot.

- [ ] **Step 6: Expor campos nas interfaces correctas**

A candidatura e a revisão administrativa mostram todos os campos. `ProfileForm.__init__` remove `show_organization_on_profile` quando a adesão não representa uma organização. Ao desligar a representação, o serviço de gravação limpa também esse consentimento no perfil. O perfil aprovado mostra nome e cargo apenas quando presentes no snapshot.

- [ ] **Step 7: Executar testes focados e de acesso**

Run: `.\.venv\Scripts\python.exe manage.py test memberships profiles.tests.test_models profiles.tests.test_membership_visibility --verbosity 2`

Expected: PASS.

- [ ] **Step 8: Commit e push**

```powershell
git add memberships profiles templates/memberships templates/moderation/membership_review.html templates/profiles
git commit -m "feat: adicionar representacao de organizacoes"
git push origin main
```

---

### Task 4: Infraestrutura e eventos de email operacional

**Files:**
- Modify: `config/settings.py`
- Modify: `.env.example`
- Create: `core/emailing.py`
- Create: `templates/emails/membership_submitted_subject.txt`
- Create: `templates/emails/membership_submitted_body.txt`
- Create: `templates/emails/membership_decision_subject.txt`
- Create: `templates/emails/membership_decision_body.txt`
- Create: `templates/emails/profile_submitted_subject.txt`
- Create: `templates/emails/profile_submitted_body.txt`
- Create: `templates/emails/profile_decision_subject.txt`
- Create: `templates/emails/profile_decision_body.txt`
- Modify: `accounts/services.py`
- Modify: `memberships/views.py`
- Modify: `moderation/services.py`
- Modify: `profiles/views.py`
- Modify: `interactions/services.py`
- Create: `tests/test_emailing.py`
- Modify: `memberships/tests/test_views.py`
- Modify: `moderation/tests/test_memberships.py`
- Modify: `moderation/tests/test_services.py`
- Modify: `interactions/tests/test_services.py`

**Interfaces:**
- Produces: `send_template_email(template_prefix, recipient_list, context) -> None`.
- Produces: settings `KALITICA_ADMIN_EMAILS` and `PUBLIC_BASE_URL`.
- Consumes: transaction hooks and existing moderation services.

- [ ] **Step 1: Escrever testes vermelhos de destinatário, conteúdo e tolerância a falhas**

```python
@override_settings(KALITICA_ADMIN_EMAILS=["equipa@nhakalitica.gw"])
def test_membership_submission_emails_the_team(self):
    self.client.post("/adesao/submeter/")
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].to, ["equipa@nhakalitica.gw"])
    self.assertIn("Nova candidatura", mail.outbox[0].subject)

@patch("core.emailing.send_mail", side_effect=RuntimeError("smtp unavailable"))
def test_email_failure_does_not_rollback_approved_membership(self, mocked_send):
    moderate_membership(self.membership, self.staff, Membership.Status.APPROVED)
    self.membership.refresh_from_db()
    self.assertEqual(self.membership.status, Membership.Status.APPROVED)
```

- [ ] **Step 2: Executar testes e confirmar falhas por ausência de emails**

Run: `.\.venv\Scripts\python.exe manage.py test tests.test_emailing memberships.tests.test_views moderation.tests.test_memberships --verbosity 2`

Expected: FAIL nos novos comportamentos.

- [ ] **Step 3: Implementar renderização e envio centralizado**

```python
def send_template_email(template_prefix, recipient_list, context):
    recipients = [item for item in recipient_list if item]
    if not recipients:
        return
    subject = render_to_string(f"emails/{template_prefix}_subject.txt", context).strip()
    body = render_to_string(f"emails/{template_prefix}_body.txt", context)
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    except Exception:
        logger.exception("Falha ao enviar email operacional", extra={"template": template_prefix})
```

- [ ] **Step 4: Agendar emails depois do commit da transacção**

Em serviços transaccionais usar:

```python
transaction.on_commit(lambda: send_template_email(
    "membership_decision",
    [membership.user.email],
    {"membership": membership, "dashboard_url": f"{settings.PUBLIC_BASE_URL}/adesao/"},
))
```

Submissões notificam `settings.KALITICA_ADMIN_EMAILS`. Decisões notificam o utilizador. Emails de contacto mantêm conteúdo mínimo e passam pelo mesmo serviço.

- [ ] **Step 5: Actualizar configuração e documentação**

`.env.example` deve incluir:

```text
PUBLIC_BASE_URL=https://nhakalitica.gw
KALITICA_CONTACT_EMAIL=info@nhakalitica.gw
KALITICA_ADMIN_EMAILS=info@nhakalitica.gw
DEFAULT_FROM_EMAIL=Kalitica Networking Society <noreply@nhakalitica.gw>
```

- [ ] **Step 6: Executar testes de email e moderação**

Run: `.\.venv\Scripts\python.exe manage.py test tests.test_emailing accounts memberships moderation interactions.tests.test_services --verbosity 2`

Expected: PASS com backend de email em memória nos testes.

- [ ] **Step 7: Commit e push**

```powershell
git add config .env.example core/emailing.py tests/test_emailing.py templates/emails accounts/services.py memberships moderation profiles/views.py interactions/services.py
git commit -m "feat: enviar emails operacionais"
git push origin main
```

---

### Task 5: Desactivação recuperável e eliminação após 30 dias

**Files:**
- Modify: `accounts/models.py`
- Create: `accounts/migrations/0004_user_deletion_schedule.py`
- Modify: `accounts/services.py`
- Modify: `accounts/views.py`
- Modify: `accounts/admin.py`
- Modify: `templates/accounts/deactivate.html`
- Create: `templates/accounts/deactivation_scheduled.html`
- Create: `accounts/management/__init__.py`
- Create: `accounts/management/commands/__init__.py`
- Create: `accounts/management/commands/purge_scheduled_accounts.py`
- Create: `accounts/tests/test_account_deletion.py`
- Modify: `accounts/tests/test_account_security.py`
- Modify: `moderation/tests/test_services.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `schedule_account_deletion(user, now=None) -> User`.
- Produces: `restore_scheduled_account(user) -> User`.
- Produces: command `purge_scheduled_accounts [--dry-run]`.

- [ ] **Step 1: Escrever testes vermelhos do ciclo de 30 dias**

```python
def test_deactivation_schedules_deletion_in_thirty_days(self):
    now = timezone.now()
    with patch("accounts.services.timezone.now", return_value=now):
        schedule_account_deletion(self.user)
    self.user.refresh_from_db()
    self.assertFalse(self.user.is_active)
    self.assertEqual(self.user.scheduled_deletion_at, now + timedelta(days=30))
    self.assertFalse(self.user.profile.is_discoverable)

def test_dry_run_does_not_delete_expired_account(self):
    call_command("purge_scheduled_accounts", "--dry-run")
    self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())

def test_command_deletes_only_expired_accounts(self):
    call_command("purge_scheduled_accounts")
    self.assertFalse(get_user_model().objects.filter(pk=self.expired_user.pk).exists())
    self.assertTrue(get_user_model().objects.filter(pk=self.future_user.pk).exists())
```

- [ ] **Step 2: Executar testes e confirmar falha pelos campos e comando inexistentes**

Run: `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_account_deletion --verbosity 2`

Expected: ERROR ou FAIL.

- [ ] **Step 3: Implementar campos, serviço de agendamento e restauração**

```python
def schedule_account_deletion(user, now=None):
    now = now or timezone.now()
    user.deletion_requested_at = now
    user.scheduled_deletion_at = now + timedelta(days=30)
    user.is_active = False
    user.save(update_fields=("deletion_requested_at", "scheduled_deletion_at", "is_active"))
    profile = user.profile
    profile.status = Profile.Status.ARCHIVED
    profile.review_status = Profile.ReviewStatus.DRAFT
    profile.is_public = False
    profile.is_discoverable = False
    profile.save(update_fields=("status", "review_status", "is_public", "is_discoverable", "updated_at"))
    return user
```

`restore_scheduled_account` só funciona antes da data agendada, limpa as datas, reactiva a conta e mantém o perfil em rascunho e invisível.

- [ ] **Step 4: Implementar comando idempotente com simulação**

Seleccionar contas inactivas com `scheduled_deletion_at__lte=timezone.now()`. Em `--dry-run`, listar apenas identificadores internos. Na execução real, apagar cada conta dentro da sua própria transacção e continuar as restantes se uma conta falhar.

- [ ] **Step 5: Integrar view, confirmação e acção administrativa**

A view usa o serviço depois de validar a palavra-passe. A página final não expõe dados privados e informa prazo, data e `info@nhakalitica.gw`. O Django admin recebe uma acção para restaurar contas ainda dentro do prazo.

- [ ] **Step 6: Executar testes de eliminação e regressão de conta**

Run: `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_account_deletion accounts.tests.test_account_security accounts.tests.test_auth --verbosity 2`

Expected: PASS.

- [ ] **Step 7: Commit e push**

```powershell
git add accounts templates/accounts README.md
git commit -m "feat: eliminar contas apos prazo de recuperacao"
git push origin main
```

---

### Task 6: Taxonomia localizada e tradução integral da interface

**Files:**
- Modify: `taxonomy/models.py`
- Create: `taxonomy/migrations/0002_localized_names.py`
- Modify: `taxonomy/admin.py`
- Modify: `taxonomy/views.py`
- Modify: `profiles/public_views.py`
- Modify: `profiles/selectors.py`
- Modify: all HTML files under `templates/` that still contain visible text outside i18n tags
- Modify: visible Python messages under `accounts/`, `memberships/`, `profiles/`, `interactions/`, `moderation/`, `taxonomy/`, `core/`
- Modify: `locale/en/LC_MESSAGES/django.po`
- Modify: `locale/fr/LC_MESSAGES/django.po`
- Modify: compiled `.mo` files
- Create: `taxonomy/tests/test_localization.py`
- Modify: `core/tests.py`
- Modify: tests for translated flows in each application

**Interfaces:**
- Produces: `NamedActiveModel.localized_name`.
- Produces: snapshots com labels de escolhas em `pt`, `fr` e `en` e títulos de notificação localizados no momento de apresentação.
- Consumes: `django.utils.translation.get_language()`.

- [ ] **Step 1: Escrever testes vermelhos para nomes localizados e páginas privadas**

```python
class TaxonomyLocalizationTests(TestCase):
def test_localized_name_uses_active_language_and_portuguese_fallback(self):
        sector = Sector.objects.create(name="Saúde", name_en="Health", name_fr="")
        with translation.override("en"):
            self.assertEqual(sector.localized_name, "Health")
        with translation.override("fr"):
            self.assertEqual(sector.localized_name, "Saúde")

def test_public_snapshot_exposes_choice_labels_for_all_languages(self):
    payload = self.profile.build_public_snapshot()
    self.assertEqual(payload["availability_labels"]["pt"], "Aberto a propostas")
    self.assertEqual(payload["availability_labels"]["en"], "Open to proposals")
    self.assertEqual(payload["availability_labels"]["fr"], "Ouvert aux propositions")
```

Adicionar testes de amostragem para conta, adesão, perfil, contactos, favoritos, taxonomia e administração em inglês e francês. Cada resposta deve conter o título traduzido e não conter o título português correspondente.

- [ ] **Step 2: Executar e confirmar falhas de localização**

Run: `.\.venv\Scripts\python.exe manage.py test taxonomy.tests.test_localization core.tests.InterfaceLanguageTests --verbosity 2`

Expected: FAIL por campos inexistentes ou texto português.

- [ ] **Step 3: Implementar campos e propriedade localizada**

O modelo abstracto `NamedActiveModel` recebe `name_en` e `name_fr`, vazios por defeito. A propriedade:

```python
@property
def localized_name(self):
    language = (get_language() or "pt").split("-", 1)[0]
    if language == "en" and self.name_en.strip():
        return self.name_en
    if language == "fr" and self.name_fr.strip():
        return self.name_fr
    return self.name
```

Views, filtros e templates usam `localized_name` para apresentação. A pesquisa textual consulta `name`, `name_en` e `name_fr` para que o utilizador encontre a mesma taxonomia em qualquer idioma. Slugs e administração mantêm `name` como referência portuguesa.

`build_public_snapshot()` passa a guardar dicionários `availability_labels`, `work_preference_labels` e `seniority_labels` com chaves `pt`, `fr` e `en`. Cada idioma é calculado dentro de `translation.override(language)`. Os idiomas do perfil guardam o código do nível e labels nas três línguas. Uma migração de dados completa estas estruturas nos snapshots aprovados existentes sem alterar o conteúdo livre dos membros.

- [ ] **Step 4: Internacionalizar os 34 templates identificados**

Adicionar `{% load i18n %}` e envolver todos os textos visíveis, títulos, labels, alternativas, estados vazios, confirmações e atributos acessíveis. Não envolver conteúdo criado por membros.

Executar uma verificação que deve terminar com zero ficheiros sem i18n, excepto templates exclusivamente estruturais sem texto visível.

- [ ] **Step 5: Internacionalizar mensagens Python e escolhas**

Usar `gettext_lazy` em modelos e formulários, `gettext` em views e serviços. Os títulos das notificações são apresentados através de uma propriedade localizada baseada em `Notification.type`. O corpo livre escrito por membros ou administradores não é traduzido automaticamente. Os emails permanecem em português por decisão aprovada.

- [ ] **Step 6: Preencher e compilar catálogos**

Run: `.\.venv\Scripts\python.exe manage.py makemessages -l en -l fr`

Preencher todas as entradas. Validar com `polib` que não existem entradas activas vazias ou fuzzy, tratando plurais como preenchidos quando todos os índices necessários existem.

Run: `.\.venv\Scripts\python.exe -c "import polib; [polib.pofile(path).save_as_mofile(path.replace('.po', '.mo')) for path in ('locale/en/LC_MESSAGES/django.po', 'locale/fr/LC_MESSAGES/django.po')]"`

- [ ] **Step 7: Executar testes de idioma e aplicações afectadas**

Run: `.\.venv\Scripts\python.exe manage.py test core taxonomy accounts memberships profiles interactions moderation --verbosity 1`

Expected: PASS.

- [ ] **Step 8: Commit e push**

```powershell
git add taxonomy profiles accounts memberships interactions moderation core templates locale
git commit -m "feat: completar interface trilingue"
git push origin main
```

---

### Task 7: Validação de fotografias e documentação de produção

**Files:**
- Modify: `profiles/forms.py`
- Modify: `profiles/tests/test_forms.py`
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `.github/workflows/tests.yml`
- Modify: `tests/test_project_configuration.py`

**Interfaces:**
- Produces: validação de fotografia com máximo de 5 MB e formatos JPEG, PNG ou WebP.
- Consumes: configuração de media existente.

- [ ] **Step 1: Escrever testes vermelhos de fotografia**

```python
def test_profile_rejects_photo_larger_than_five_megabytes(self):
    upload = SimpleUploadedFile("photo.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg")
    form = ProfileForm(data=self.valid_data(), files={"photo": upload}, instance=self.profile)
    self.assertFalse(form.is_valid())
    self.assertIn("photo", form.errors)

def test_profile_rejects_unsupported_photo_type(self):
    upload = SimpleUploadedFile("photo.gif", b"GIF89a", content_type="image/gif")
    form = ProfileForm(data=self.valid_data(), files={"photo": upload}, instance=self.profile)
    self.assertFalse(form.is_valid())
```

- [ ] **Step 2: Executar e confirmar falha por ausência de validação**

Run: `.\.venv\Scripts\python.exe manage.py test profiles.tests.test_forms --verbosity 2`

Expected: FAIL nos novos testes.

- [ ] **Step 3: Implementar validação mínima**

`clean_photo()` valida tamanho, extensão e `content_type`. Pillow mantém a validação estrutural fornecida pelo `ImageField`.

- [ ] **Step 4: Documentar operação de produção**

O README deve incluir configuração de PostgreSQL, SMTP, domínio, SSL, media persistente ou object storage, cópia de segurança, teste de restauração, comando diário `purge_scheduled_accounts` e criação do primeiro administrador.

O workflow deve executar `check`, migrações, testes e detecção de artefactos de codificação.

- [ ] **Step 5: Executar testes e checks**

Run: `.\.venv\Scripts\python.exe manage.py test profiles.tests.test_forms tests.test_project_configuration --verbosity 2`

Run: `.\.venv\Scripts\python.exe manage.py check --deploy` com variáveis de produção temporárias.

Expected: PASS e zero avisos de deployment.

- [ ] **Step 6: Commit e push**

```powershell
git add profiles/forms.py profiles/tests/test_forms.py .env.example README.md .github/workflows/tests.yml tests/test_project_configuration.py
git commit -m "chore: reforcar preparacao de producao"
git push origin main
```

---

### Task 8: Verificação integral e aceitação do lançamento

**Files:**
- Modify only when verification reveals a defect, always starting with a failing regression test.

**Interfaces:**
- Consumes: all deliverables from Tasks 1 through 7.
- Produces: verified launch candidate on `main`.

- [ ] **Step 1: Validar migrações e dependências**

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

Expected: `No changes detected` and `No broken requirements found`.

- [ ] **Step 2: Executar suite completa**

Run: `.\.venv\Scripts\python.exe -u manage.py test --verbosity 1`

Expected: todos os testes passam sem erros.

- [ ] **Step 3: Validar configuração de produção**

Definir temporariamente `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS=nhakalitica.gw,www.nhakalitica.gw`, `CSRF_TRUSTED_ORIGINS=https://nhakalitica.gw,https://www.nhakalitica.gw`, `PUBLIC_BASE_URL=https://nhakalitica.gw` e executar:

Run: `.\.venv\Scripts\python.exe manage.py check --deploy`

Expected: zero problemas.

- [ ] **Step 4: Validar catálogos e texto**

Usar `polib` para confirmar zero entradas activas vazias ou fuzzy em inglês e francês. Procurar artefactos `Ã`, `Â`, `â€™`, `??` e os contactos antigos fora de migrações de reparação e testes específicos.

- [ ] **Step 5: Rever os percursos no navegador**

Inspeccionar a 1440, 768 e 375 píxeis:

1. visitante em português, francês e inglês
2. registo e páginas legais
3. candidatura pessoal e candidatura como representante
4. revisão e aprovação administrativa
5. publicação privada e publicação autorizada da organização
6. pesquisa, favoritos, contacto e denúncia
7. desactivação e confirmação do prazo

Confirmar foco visível, ausência de deslocamento horizontal, labels, erros, estados vazios e consola sem erros. Se o navegador automatizado bloquear o endereço local, executar esta revisão manualmente no navegador aberto pelo utilizador e registar a limitação sem contornar a política.

- [ ] **Step 6: Confirmar Git e GitHub**

```powershell
git diff --check
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
gh run list --repo atchutchi/nhakalitica.gw --limit 1
```

Expected: árvore limpa, hashes local e remoto iguais e workflow mais recente concluído com sucesso.

- [ ] **Step 7: Corrigir apenas falhas verificadas**

Para cada defeito, escrever primeiro um teste que reproduza a falha, confirmar vermelho, implementar a correcção mínima, confirmar verde e repetir a suite relevante.

- [ ] **Step 8: Commit e push final, apenas se houver correcções**

Confirmar com `git status --short` que todos os ficheiros modificados pertencem exclusivamente às correcções desta tarefa. Adicionar esses caminhos de forma explícita, criar o commit `fix: concluir verificacao de lancamento` e executar `git push origin main`.
