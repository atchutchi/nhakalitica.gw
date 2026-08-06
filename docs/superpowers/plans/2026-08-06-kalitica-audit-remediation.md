# Kalitica Audit Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir integralmente os 16 problemas confirmados na auditoria de produção e substituir a gestão técnica de utilizadores por uma página própria de Membros na Administração Kalitica.

**Architecture:** As correcções mantêm a arquitectura Django existente. As regras de negócio ficam em serviços Python transaccionais, as views apenas validam pedidos e preparam contexto e os templates recebem estados explícitos. A administração personalizada continua protegida por `staff_required`. A recuperação de conta reutiliza `accounts.services.restore_scheduled_account` e regista cada acção em `moderation.models.AuditLog`.

**Tech Stack:** Django, templates Django, CSS, JavaScript sem framework, gettext, SQLite nos testes e PostgreSQL em produção.

## Global Constraints

- Preservar o acesso à rede apenas para adesões aprovadas.
- Não publicar automaticamente um perfil quando uma conta é restaurada.
- Executar qualquer alteração administrativa por POST com CSRF.
- Não expor dados privados em páginas públicas ou mensagens de erro.
- Traduzir toda a interface nova para português, francês e inglês.
- Criar primeiro um teste que falhe para cada comportamento corrigido.
- Fazer commits pequenos e publicar apenas depois de a suite completa passar.

---

### Task 1: Corrigir a entrada pública, contraste e menus móveis

**Files:**
- Modify: `core/tests.py`
- Modify: `accounts/tests/test_auth.py`
- Modify: `templates/core/home.html`
- Modify: `templates/registration/signup_closed.html`
- Modify: `templates/core/_public_header.html`
- Modify: `templates/base.html`
- Modify: `static/js/navigation.js`
- Modify: `static/css/public.css`
- Modify: `static/css/app-shell.css`

- [ ] **Step 1: Escrever testes que cubram os problemas públicos**

Adicionar testes que confirmem que a página inicial apresenta o aviso de registos encerrados antes das acções do hero quando `PUBLIC_SIGNUP_ENABLED=False`, que o CTA não promete um registo disponível e que o título do cartão azul usa uma classe ou regra de contraste explícita. Confirmar também que os botões dos menus público e privado têm texto acessível actualizável.

- [ ] **Step 2: Executar os testes específicos e confirmar a falha**

Run: `python manage.py test core.tests accounts.tests.test_auth`

Expected: falha nas novas asserções porque o aviso ainda só existe na página de registo e os menus mantêm sempre o texto “Abrir menu”.

- [ ] **Step 3: Implementar a correcção mínima**

Na home, usar `settings.PUBLIC_SIGNUP_ENABLED` através do contexto existente ou de uma condição preparada pela view. Quando o registo estiver fechado, mostrar no topo do hero um aviso claro e substituir “Pedir adesão” por uma acção coerente para entrar. Manter a página `signup_closed.html` como destino seguro.

No JavaScript, actualizar `aria-expanded` e o conteúdo do elemento `.visually-hidden` entre as traduções fornecidas por atributos `data-open-label` e `data-close-label`. Aplicar a mesma função aos menus público e privado. Adicionar foco turquesa visível e garantir contraste branco no título do cartão azul.

- [ ] **Step 4: Executar novamente os testes específicos**

Run: `python manage.py test core.tests accounts.tests.test_auth`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add core/tests.py accounts/tests/test_auth.py templates/core/home.html templates/registration/signup_closed.html templates/core/_public_header.html templates/base.html static/js/navigation.js static/css/public.css static/css/app-shell.css && git commit -m "Corrigir entrada publica e menus moveis"`

### Task 2: Corrigir estados e acções da área de membro

**Files:**
- Modify: `accounts/tests/test_auth.py`
- Modify: `profiles/tests/test_views.py`
- Modify: `interactions/tests/test_views.py`
- Modify: `core/tests.py`
- Modify: `templates/accounts/dashboard.html`
- Modify: `templates/settings_base.html`
- Modify: `templates/interactions/contacts.html`
- Modify: `templates/interactions/favorites.html`
- Modify: `templates/taxonomy/area_list.html`
- Modify: `static/css/settings.css`
- Modify: `static/css/app-shell.css`

- [ ] **Step 1: Escrever testes dos estados reais do membro**

Cobrir os quatro estados de visibilidade no painel: publicado e pesquisável, aprovado mas oculto por opção, em revisão e rascunho ou correcções. Os testes devem validar mensagens diferentes e nunca afirmar que um perfil está visível apenas porque `is_discoverable=True` sem o restante contrato de publicação.

Adicionar testes para `aria-current="page"` na secção correcta das definições, para os estados vazios de mensagens com CTA para o Directório, para a ausência do botão de comparação quando existem menos de dois favoritos e para a ligação `mailto:info@nhakalitica.gw` nas Áreas.

- [ ] **Step 2: Executar os testes específicos e confirmar a falha**

Run: `python manage.py test accounts.tests.test_auth profiles.tests.test_views interactions.tests.test_views core.tests`

Expected: falha nas mensagens, navegação activa, comparação e contacto das Áreas.

- [ ] **Step 3: Implementar mensagens e navegação baseadas no estado real**

No painel, avaliar `profile.is_visible_to_members` ou a combinação de estado aprovada pelo modelo. Mostrar mensagens próprias para perfil visível, perfil aprovado mas oculto, perfil em revisão e perfil ainda não submetido.

Em `settings_base.html`, determinar o item activo com `request.resolver_match.url_name` e `request.resolver_match.namespace`. Aplicar `is-active` e `aria-current="page"` apenas ao destino actual. No CSS móvel, permitir quebra e deslocamento apenas dentro da navegação, sem criar uma barra horizontal permanente na página.

Nos contactos, usar o mesmo componente de estado vazio nas duas colunas e acrescentar “Pesquisar profissionais”. Nos favoritos, mostrar o formulário de comparação apenas com pelo menos dois itens. Nas Áreas, transformar o contacto em ligação de email e explicar que a sugestão será revista.

- [ ] **Step 4: Executar novamente os testes específicos**

Run: `python manage.py test accounts.tests.test_auth profiles.tests.test_views interactions.tests.test_views core.tests`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add accounts/tests/test_auth.py profiles/tests/test_views.py interactions/tests/test_views.py core/tests.py templates/accounts/dashboard.html templates/settings_base.html templates/interactions/contacts.html templates/interactions/favorites.html templates/taxonomy/area_list.html static/css/settings.css static/css/app-shell.css && git commit -m "Corrigir estados e acoes da area de membro"`

### Task 3: Tornar a administração coerente e acessível

**Files:**
- Modify: `moderation/tests/test_views.py`
- Modify: `moderation/views.py`
- Modify: `templates/moderation/base_admin.html`
- Modify: `templates/moderation/membership_list.html`
- Modify: `templates/moderation/profile_list.html`
- Modify: `templates/moderation/report_list.html`
- Modify: `templates/moderation/profile_review.html`
- Modify: `templates/moderation/audit_list.html`
- Modify: `static/css/admin.css`

- [ ] **Step 1: Escrever testes de navegação, filtros e decisões válidas**

Confirmar que a administração mostra “Voltar à rede”, um formulário POST de saída e a secção activa com `aria-current="page"`. Confirmar labels associados aos filtros e pesquisa. Para cada estado de perfil, confirmar que a view só fornece acções incluídas em `ACTION_CONFIG[action]["allowed"]`. Um perfil aprovado não pode apresentar “Aprovar publicação”.

Adicionar uma asserção estrutural para os atributos `data-label` das células da Auditoria que suportam a apresentação responsiva.

- [ ] **Step 2: Executar os testes e confirmar a falha**

Run: `python manage.py test moderation.tests.test_views moderation.tests.test_services moderation.tests.test_reports`

Expected: falha porque a navegação não tem estado activo, os filtros não têm labels e a revisão recebe todas as acções.

- [ ] **Step 3: Implementar o shell e as acções válidas**

Criar um pequeno helper em `moderation.views` que devolva apenas as acções permitidas para o estado actual. Passar essas acções ao template e iterá-las sem duplicar regras. No shell, usar `request.resolver_match.url_name` para a ligação activa. Adicionar ligação para a rede, formulário de logout POST e, apenas para superutilizadores, ligação secundária para “Administração técnica”.

Adicionar labels visuais ou `visually-hidden` a todos os controlos. Na Auditoria, acrescentar `data-label` localizado em cada célula e converter as linhas em cartões abaixo do breakpoint móvel sem scroll horizontal obrigatório.

- [ ] **Step 4: Executar novamente os testes específicos**

Run: `python manage.py test moderation.tests.test_views moderation.tests.test_services moderation.tests.test_reports`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add moderation/tests/test_views.py moderation/views.py templates/moderation/base_admin.html templates/moderation/membership_list.html templates/moderation/profile_list.html templates/moderation/report_list.html templates/moderation/profile_review.html templates/moderation/audit_list.html static/css/admin.css && git commit -m "Melhorar navegacao e acessibilidade administrativa"`

### Task 4: Criar a página própria de Membros

**Files:**
- Modify: `moderation/urls.py`
- Modify: `moderation/views.py`
- Modify: `moderation/tests/test_views.py`
- Modify: `accounts/tests/test_account_deletion.py`
- Create: `templates/moderation/member_list.html`
- Create: `templates/moderation/member_detail.html`
- Modify: `templates/moderation/base_admin.html`
- Modify: `static/css/admin.css`

- [ ] **Step 1: Escrever testes de autorização, pesquisa, filtros e detalhe**

Testar que visitantes e membros comuns não acedem à lista. Um membro de staff deve conseguir pesquisar por nome e email e filtrar por conta activa ou inactiva, tipo de membro e estado da adesão. A lista deve apresentar o estado da conta, adesão e publicação sem expor campos desnecessários.

O detalhe deve mostrar email confirmado, datas de eliminação, adesão, perfil e ligações para as revisões correspondentes. A acção de recuperação deve rejeitar GET, exigir staff e restaurar apenas uma conta inactiva ainda dentro dos 30 dias.

- [ ] **Step 2: Escrever o teste da recuperação administrativa e confirmar a falha**

Depois de `schedule_account_deletion`, fazer POST para `moderation:member-restore`. Confirmar `is_active=True`, datas limpas, perfil em rascunho privado e um `AuditLog` com `action="account.deletion_restored"`, actor e identificador do utilizador.

Run: `python manage.py test moderation.tests.test_views accounts.tests.test_account_deletion`

Expected: erro de URL ou 404 porque as páginas e a acção ainda não existem.

- [ ] **Step 3: Implementar URLs e views**

Adicionar:

```python
path("membros/", member_list, name="member-list")
path("membros/<int:pk>/", member_detail, name="member-detail")
path("membros/<int:pk>/restaurar/", member_restore, name="member-restore")
```

Em `member_list`, começar em `User.objects.select_related("membership", "profile")`, aplicar pesquisa com `Q(email__icontains=...)`, `Q(first_name__icontains=...)` e `Q(last_name__icontains=...)` e validar cada filtro contra os choices do modelo. Ordenar por nome e email.

Em `member_detail`, carregar as mesmas relações e preparar ligações de revisão apenas quando existem. Em `member_restore`, usar `@require_POST`, chamar `restore_scheduled_account`, transformar `ValidationError` em mensagem clara e criar o registo de auditoria só depois da recuperação bem sucedida. Redireccionar para o detalhe.

- [ ] **Step 4: Implementar templates e estilos**

Criar lista com pesquisa, filtros nomeados e linhas legíveis em desktop e mobile. Criar detalhe por secções: Conta, Adesão e Perfil. Mostrar o formulário de recuperação apenas quando `not user.is_active`, `scheduled_deletion_at` existe e ainda não expirou. Exigir confirmação JavaScript através do mecanismo administrativo já existente.

Alterar a ligação “Membros” do menu para `moderation:member-list`. Manter “Administração técnica” fora da navegação principal e apenas para superutilizadores.

- [ ] **Step 5: Executar novamente os testes específicos**

Run: `python manage.py test moderation.tests.test_views accounts.tests.test_account_deletion`

Expected: PASS.

- [ ] **Step 6: Commit**

Run: `git add moderation/urls.py moderation/views.py moderation/tests/test_views.py accounts/tests/test_account_deletion.py templates/moderation/member_list.html templates/moderation/member_detail.html templates/moderation/base_admin.html static/css/admin.css && git commit -m "Criar gestao administrativa de membros"`

### Task 5: Criar páginas de erro coerentes e seguras

**Files:**
- Modify: `core/tests.py`
- Create: `core/error_views.py`
- Create: `templates/403.html`
- Create: `templates/403_csrf.html`
- Modify: `config/settings.py`
- Modify: `static/css/auth.css`

- [ ] **Step 1: Escrever testes para 403 e CSRF**

Usar `Client(enforce_csrf_checks=True)` para submeter um formulário sem token e confirmar status 403, marca Kalitica, explicação não técnica e botão “Actualizar e tentar novamente”. Confirmar também que um utilizador sem permissão recebe uma página 403 com ligação segura para voltar.

- [ ] **Step 2: Executar os testes e confirmar a falha**

Run: `python manage.py test core.tests`

Expected: falha porque Django devolve a página técnica padrão.

- [ ] **Step 3: Implementar handlers sem expor detalhes internos**

Criar uma view CSRF com assinatura `csrf_failure(request, reason="")` que não apresenta `reason`. Configurar `CSRF_FAILURE_VIEW = "core.error_views.csrf_failure"`. Criar `templates/403.html` para permissões e `templates/403_csrf.html` para formulário expirado. Reutilizar a identidade visual e fornecer acções para voltar ou recarregar.

- [ ] **Step 4: Executar novamente os testes específicos**

Run: `python manage.py test core.tests`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add core/tests.py core/error_views.py templates/403.html templates/403_csrf.html config/settings.py static/css/auth.css && git commit -m "Personalizar erros de permissao e formularios"`

### Task 6: Traduzir, validar e preparar a publicação

**Files:**
- Modify: `locale/en/LC_MESSAGES/django.po`
- Modify: `locale/fr/LC_MESSAGES/django.po`
- Modify: `locale/en/LC_MESSAGES/django.mo`
- Modify: `locale/fr/LC_MESSAGES/django.mo`
- Modify: `docs/audits/2026-08-05-production/README.md`

- [ ] **Step 1: Extrair e preencher todas as mensagens novas**

Run: `python manage.py makemessages -l en -l fr --no-wrap`

Preencher cada `msgstr` novo em francês e inglês. Não deixar traduções vazias nem marcadas como fuzzy.

- [ ] **Step 2: Compilar e validar os catálogos**

Run: `python manage.py compilemessages`

Run: `rg -n "#, fuzzy|msgstr \"\"$" locale/en/LC_MESSAGES/django.po locale/fr/LC_MESSAGES/django.po`

Expected: apenas os `msgstr ""` estruturais dos cabeçalhos ou mensagens multilinha. Nenhuma tradução nova vazia e nenhum fuzzy.

- [ ] **Step 3: Executar verificações técnicas completas**

Run: `python manage.py check --deploy`

Run: `python manage.py test`

Run: `git diff --check`

Expected: sem erros de sistema, suite completa PASS e nenhum problema de whitespace.

- [ ] **Step 4: Validar a interface nos três papéis e idiomas**

Validar como visitante, membro aprovado e administrador em português, francês e inglês. Cobrir desktop, largura intermédia e mobile. Confirmar teclado, foco, menu, ausência de overflow global, estados vazios, filtros, decisões válidas, lista e detalhe de Membros, 403 e CSRF. Não executar recuperações destrutivas em produção. Usar apenas a conta de demonstração preparada para esse teste ou validar a recuperação localmente.

- [ ] **Step 5: Actualizar o relatório de auditoria**

Em `docs/audits/2026-08-05-production/README.md`, marcar cada problema como corrigido com referência ao teste e à página validada. Registar limitações reais se alguma validação visual não puder ser repetida.

- [ ] **Step 6: Commit final de traduções e evidência**

Run: `git add locale/en/LC_MESSAGES/django.po locale/fr/LC_MESSAGES/django.po locale/en/LC_MESSAGES/django.mo locale/fr/LC_MESSAGES/django.mo docs/audits/2026-08-05-production/README.md && git commit -m "Concluir traducoes e validacao da auditoria"`

- [ ] **Step 7: Publicar e confirmar produção**

Run: `git push origin main`

Aguardar o deployment Railway e confirmar `/saude/`, a home, o painel do membro, `/administracao/` e `/administracao/membros/`. Não declarar conclusão antes de a versão publicada responder correctamente.
