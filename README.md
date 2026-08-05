# Kalitica Networking Society

Rede profissional privada para membros aprovados da Kalitica na Guiné-Bissau, na diáspora e entre profissionais com uma ligação relevante ao país.

## Requisitos

Python 3.12 ou superior. O desenvolvimento local usa SQLite. Ambientes partilhados usam PostgreSQL.

## Instalação local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

A aplicação fica disponível em `http://127.0.0.1:8000/`.

## Configuração

As variáveis suportadas estão documentadas em `.env.example`. O projecto lê as variáveis do processo.

Define `PUBLIC_BASE_URL=https://nhakalitica.gw` para gerar ligações canónicas com o domínio oficial e `KALITICA_CONTACT_EMAIL=info@nhakalitica.gw` para centralizar o contacto público e legal.

Define `KALITICA_ADMIN_EMAILS` com um ou mais endereços separados por vírgulas. Estes destinatários recebem avisos de novas candidaturas e novos perfis. As decisões são enviadas directamente ao membro e os pedidos de contacto nunca incluem a mensagem privada no email.

Para PostgreSQL, define `DATABASE_ENGINE=postgresql` e preenche `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST` e `DATABASE_PORT`.

## Testes

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

As traduções compiladas são geradas com `polib`, disponível nas dependências de desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Estrutura

`core` contém páginas institucionais e endpoints operacionais. `accounts` gere autenticação e confirmação de email. `memberships` gere adesões e acesso à rede. `profiles` gere perfis profissionais e publicação. `taxonomy` organiza sectores, áreas, especializações e competências. `moderation` concentra decisões administrativas e auditoria. `interactions` gere favoritos, comparação, contactos, denúncias e notificações.

## Estado actual

A base Django foi importada do CVLink como ponto de partida independente. A implementação da adesão, da rede privada, dos três idiomas e do design aprovado está organizada em `docs/superpowers/plans/2026-07-26-kalitica-networking-society.md`.

## Administração

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

A administração Django fica em `http://127.0.0.1:8000/admin/`.

## Segurança de produção

Quando `DEBUG=False`, `SECRET_KEY` é obrigatória. Define também `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

```powershell
$env:DEBUG='False'
$env:SECRET_KEY='uma-chave-longa-e-aleatoria'
$env:ALLOWED_HOSTS='nhakalitica.gw,www.nhakalitica.gw'
$env:CSRF_TRUSTED_ORIGINS='https://nhakalitica.gw,https://www.nhakalitica.gw'
.\.venv\Scripts\python.exe manage.py check --deploy
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

O endpoint `/saude/` valida a aplicação e a ligação à base de dados. Em produção usa um servidor WSGI ou ASGI, armazenamento persistente para ficheiros e cópias de segurança.

## Eliminação de contas

A desactivação agenda a eliminação dos dados pessoais após 30 dias. Antes de configurar a execução periódica, valida as contas elegíveis sem alterar dados:

```powershell
.\.venv\Scripts\python.exe manage.py purge_scheduled_accounts --dry-run
```

Em produção, executa diariamente o comando sem `--dry-run`. O comando elimina apenas contas inactivas cujo prazo terminou, processa cada conta numa transacção própria e mantém os registos administrativos legalmente necessários sem o vínculo ao utilizador eliminado.
