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

Define `MEDIA_ROOT` para um volume persistente fora do contentor da aplicação. As fotografias e os currículos não podem depender do disco temporário de uma instância. A versão inicial suporta um volume persistente local. Se a infraestrutura não garantir persistência, configura um backend de object storage compatível com Django antes do lançamento.

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

## Publicação em produção

O ambiente de produção deve disponibilizar PostgreSQL, SMTP autenticado, TLS para `nhakalitica.gw` e `www.nhakalitica.gw`, um volume persistente para `MEDIA_ROOT` e um proxy ou CDN para servir `STATIC_ROOT`. Os ficheiros de media devem permanecer privados e ser entregues apenas pelos endpoints autorizados da aplicação ou por ligações temporárias de um object storage privado. Não exponhas `MEDIA_ROOT` como pasta pública. Não uses SQLite nem o servidor `runserver` em produção.

Instala e prepara cada versão com:

```powershell
python -m pip install -r requirements.txt
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
```

Inicia a aplicação num servidor Linux com:

```text
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
```

Cria o primeiro administrador apenas numa consola protegida:

```powershell
python manage.py createsuperuser
```

Antes de abrir o registo ao público confirma estes pontos:

1. `DEBUG=False` e `SECRET_KEY` contém uma chave longa, aleatória e exclusiva.
2. `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `PUBLIC_BASE_URL` usam o domínio oficial.
3. A migração da base de dados e `collectstatic` terminaram sem erros.
4. O envio SMTP foi testado com confirmação de email, decisão de adesão e pedido de contacto.
5. O volume de media continua acessível depois de reiniciar ou substituir a instância.
6. O endpoint `/saude/` responde com sucesso através de HTTPS.
7. Os acessos ao painel administrativo e aos registos do fornecedor estão limitados à equipa autorizada.

## Cópias de segurança e recuperação

Cria diariamente uma cópia cifrada da base PostgreSQL e do volume de media. Mantém pelo menos uma cópia fora do fornecedor principal. A retenção deve respeitar a política de privacidade e não prolongar dados pessoais sem fundamento.

Testa a restauração num ambiente isolado antes do lançamento e depois em intervalos regulares. Um backup que nunca foi restaurado não constitui prova de recuperação. O teste deve confirmar a base de dados, as fotografias, os currículos, o acesso administrativo e o endpoint `/saude/`. Regista a data, a duração e o resultado do teste.

## Operações agendadas

Executa diariamente, através do agendador do fornecedor, o comando:

```text
python manage.py purge_scheduled_accounts
```

Executa primeiro com `--dry-run` em cada ambiente novo. Monitoriza o código de saída e conserva o registo operacional do processo. Não registes conteúdo pessoal eliminado nos logs.

## Eliminação de contas

A desactivação agenda a eliminação dos dados pessoais após 30 dias. Antes de configurar a execução periódica, valida as contas elegíveis sem alterar dados:

```powershell
.\.venv\Scripts\python.exe manage.py purge_scheduled_accounts --dry-run
```

Em produção, executa diariamente o comando sem `--dry-run`. O comando elimina apenas contas inactivas cujo prazo terminou, processa cada conta numa transacção própria e mantém os registos administrativos legalmente necessários sem o vínculo ao utilizador eliminado.
