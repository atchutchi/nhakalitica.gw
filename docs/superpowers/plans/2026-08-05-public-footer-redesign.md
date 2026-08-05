# Public Footer Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar o rodapé público da Kalitica numa composição institucional responsiva e acessível.

**Architecture:** O template Django passa a expor três grupos semânticos e uma linha inferior. O CSS usa Grid em desktop e tablet, Flexbox dentro dos grupos e os tokens existentes para espaçamento. Um teste de resposta protege a estrutura e o conteúdo essencial.

**Tech Stack:** Django templates, Django TestCase, CSS Grid e Flexbox

## Global Constraints

- Manter português, francês e inglês.
- Usar apenas a escala de 4, 8, 16, 24, 32 e 48 píxeis.
- Manter WCAG AA, foco visível e alvos interactivos com pelo menos 44 píxeis.
- Não alterar o fluxo de autenticação ou o funcionamento do selector de idioma.

---

### Task 1: Estrutura semântica do rodapé

**Files:**
- Modify: `templates/core/_public_footer.html`
- Test: `tests/test_core.py`

**Interfaces:**
- Consumes: `LANGUAGES`, `LANGUAGE_CODE` e rotas legais Django existentes.
- Produces: `.public-footer-grid`, `.public-footer-brand`, `.public-footer-nav`, `.public-footer-meta` e `.public-footer-bottom`.

- [x] **Step 1: Escrever um teste que exija os três grupos, os títulos e a linha inferior**
- [x] **Step 2: Executar o teste e confirmar a falha por ausência da nova estrutura**
- [x] **Step 3: Actualizar o template com a estrutura mínima aprovada**
- [x] **Step 4: Executar o teste e confirmar que passa**

### Task 2: Layout responsivo e acabamento

**Files:**
- Modify: `static/css/public.css`

**Interfaces:**
- Consumes: classes produzidas pelo template e tokens de `static/css/tokens.css`.
- Produces: grelha de três colunas, transição para tablet e empilhamento móvel.

- [x] **Step 1: Substituir o layout flexível actual pela grelha de três áreas**
- [x] **Step 2: Aplicar espaçamento, tipografia, estados interactivos e divisores**
- [x] **Step 3: Adicionar os breakpoints de tablet e telemóvel**
- [x] **Step 4: Executar o detector de layout e corrigir todos os achados do rodapé**

### Task 3: Verificação e publicação

**Files:**
- Modify: nenhum ficheiro adicional previsto

**Interfaces:**
- Consumes: aplicação Django e serviço Railway existentes.
- Produces: alteração testada, commit publicado e produção verificada.

- [x] **Step 1: Executar o teste focalizado e a suite completa**
- [x] **Step 2: Executar `python manage.py check`**
- [x] **Step 3: Verificar visualmente desktop, tablet e telemóvel**
- [x] **Step 4: Fazer commit e push para a branch principal**
- [x] **Step 5: Confirmar a versão publicada e o estado HTTP**

## Self-review

O plano cobre toda a composição aprovada, não introduz dependências e mantém o selector de idioma e as rotas existentes. Não existem marcadores de trabalho futuro nem alterações fora do rodapé público.
