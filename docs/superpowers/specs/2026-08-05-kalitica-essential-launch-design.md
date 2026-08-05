# Kalitica Essential Launch Design

## Objectivo

Concluir o primeiro lançamento da Kalitica Networking Society em `nhakalitica.gw` sem pagamentos, vagas, contas empresariais separadas ou outras funcionalidades da segunda fase.

O lote obrigatório cobre quatro áreas: experiência integral em português, francês e inglês, documentos e consentimentos legais, emails operacionais em português e representação de organizações por membros aprovados. Inclui ainda o encerramento seguro de contas com um prazo de recuperação de 30 dias.

## Decisões aprovadas

- O domínio oficial é `nhakalitica.gw`.
- A entidade responsável provisória é Kalitica Networking Society.
- O contacto oficial é `info@nhakalitica.gw`.
- A interface e os documentos legais existem integralmente em português, francês e inglês.
- Os emails automáticos são enviados apenas em português.
- Os dados de representação de uma organização são privados durante a candidatura.
- O membro pode autorizar separadamente a publicação do nome da organização e do cargo no perfil.
- Uma organização não tem uma conta autónoma. O seu representante precisa sempre de uma adesão pessoal aprovada.
- A desactivação bloqueia imediatamente a conta e inicia um prazo de recuperação de 30 dias.
- Depois dos 30 dias, os dados pessoais são eliminados ou anonimizados. Permanecem apenas os registos administrativos estritamente necessários.
- Pagamentos, vagas, equipas de recrutamento e facturação continuam fora do primeiro lançamento.

## 1. Experiência trilingue

Todas as páginas e mensagens visíveis da aplicação devem respeitar o idioma activo, incluindo conta, autenticação, adesão, perfil, pesquisa, áreas, favoritos, comparação, contactos, notificações, denúncias e administração.

Os templates usam os mecanismos de internacionalização do Django. As mensagens produzidas em Python, rótulos dos formulários, escolhas dos modelos, validações e mensagens de sucesso ou erro também são traduzíveis.

Os catálogos `pt`, `fr` e `en` não podem conter entradas vazias ou marcadas como provisórias. Os ficheiros compilados fazem parte do repositório.

A taxonomia profissional é conteúdo administrado pela plataforma e não conteúdo livre de membros. `Sector`, `Area`, `Specialization` e `Skill` passam a suportar nomes em português, francês e inglês, com português como valor obrigatório e como alternativa quando uma tradução não estiver preenchida. Slugs e relações permanecem independentes do idioma.

O conteúdo livre escrito pelos membros não é traduzido automaticamente.

## 2. Documentos legais

São criadas três páginas públicas:

- `/termos/` para os Termos de Utilização
- `/privacidade/` para a Política de Privacidade
- `/codigo-de-conduta/` para o Código de Conduta

Cada página usa a navegação pública, inclui a versão `1.0`, a data de entrada em vigor de 5 de Agosto de 2026 e o contacto `info@nhakalitica.gw`. O conteúdo integral é traduzido para francês e inglês.

Os Termos de Utilização explicam elegibilidade, natureza privada da rede, aprovação manual, exactidão da informação, conduta, moderação, suspensão, propriedade do conteúdo, ausência de cobrança no lançamento e alterações dos termos.

A Política de Privacidade identifica a Kalitica Networking Society como responsável provisória. Explica categorias de dados, finalidades, visibilidade, partilha de contactos, currículos, conservação, segurança, direitos do titular, transferências e contacto.

O Código de Conduta proíbe assédio, fraude, falsidade, discriminação, spam, recolha abusiva de dados e uso indevido de informação da rede. Explica denúncia, análise e consequências.

O rodapé, o registo, a candidatura e a submissão do perfil apontam para estes documentos. Não é apresentado um aviso de cookies enquanto a aplicação usar apenas cookies estritamente necessários e não tiver medição ou publicidade de terceiros.

Os textos são conteúdo operacional de lançamento e devem receber revisão jurídica final antes da abertura pública.

## 3. Registo de consentimentos

É criado o modelo `LegalAcceptance` com:

- utilizador
- tipo de documento: termos, privacidade ou código de conduta
- versão do documento
- origem: registo, candidatura ou publicação do perfil
- data e hora da aceitação

O modelo não guarda endereços IP em bruto. Cada combinação de utilizador, documento, versão e origem é única.

No registo, a aceitação dos Termos e da Política de Privacidade cria duas entradas. Na submissão da candidatura são registadas a Política de Privacidade e o Código de Conduta. Na submissão do perfil são registados os Termos e a Política de Privacidade.

Os campos históricos já existentes no perfil continuam preenchidos para compatibilidade, mas `LegalAcceptance` torna-se o registo auditável principal.

## 4. Representação de organizações

A candidatura recebe os campos:

- `represents_organization`, booleano
- `organization_name`, nome da organização
- `organization_role`, cargo ou função do representante
- `organization_purpose`, finalidade da utilização da rede em nome da organização

Quando `represents_organization` estiver activo, os três campos de texto são obrigatórios. Quando estiver inactivo, os campos são limpos para evitar conservação acidental.

Estes dados aparecem apenas na candidatura e na área administrativa. Não são expostos na pesquisa, no perfil ou nas exportações privadas por defeito.

O perfil recebe `show_organization_on_profile`. Este consentimento só produz efeito quando a adesão está aprovada, a candidatura indica representação de uma organização e o perfil é aprovado para publicação.

Quando autorizado, a versão pública aprovada do perfil inclui apenas `organization_name` e `organization_role`. A finalidade da representação nunca é publicada.

O acesso à pesquisa de talentos continua dependente da adesão pessoal aprovada. Não são criadas permissões especiais para organizações.

## 5. Emails operacionais

Os emails usam templates de assunto e corpo em texto simples, sempre em português. O remetente por defeito é `Kalitica Networking Society <noreply@nhakalitica.gw>`.

A variável `KALITICA_ADMIN_EMAILS` contém a lista de destinatários operacionais. A variável `PUBLIC_BASE_URL` contém `https://nhakalitica.gw` e é usada para gerar ligações fora de um pedido HTTP.

São enviados emails nos seguintes eventos:

- confirmação e reenvio de email
- nova candidatura submetida, para a equipa
- candidatura em análise, correcções, aprovação, recusa ou suspensão, para o candidato
- novo perfil submetido, para a equipa
- aprovação, correcções, rejeição, suspensão ou restauro do perfil, para o membro
- novo pedido de contacto, para o destinatário

O envio ocorre depois da confirmação da transacção da base de dados. Uma falha do fornecedor de email não reverte uma decisão administrativa já gravada. A falha é registada nos logs para intervenção da equipa.

O ambiente local continua a poder usar o backend de consola. Produção exige SMTP real configurado por variáveis de ambiente.

## 6. Desactivação e eliminação após 30 dias

O utilizador recebe `deletion_requested_at` e `scheduled_deletion_at`.

Ao confirmar a desactivação com a palavra-passe:

- a conta fica inactiva imediatamente
- o perfil deixa de estar visível
- a data de eliminação é definida para 30 dias depois
- é criado um evento de auditoria sem copiar dados pessoais para os metadados
- o utilizador vê uma confirmação que explica o prazo e o contacto de recuperação

A equipa pode restaurar a conta durante o prazo. A restauração limpa as datas de eliminação, reactiva a conta e coloca o perfil em rascunho, não público e não pesquisável. A restauração nunca publica automaticamente um perfil suspenso ou arquivado.

O comando `purge_scheduled_accounts` suporta execução normal e `--dry-run`. Elimina contas cujo prazo terminou e deixa as chaves estrangeiras de auditoria como nulas quando o modelo já permite essa conservação. Antes da eliminação, qualquer metadado administrativo que contenha dados pessoais é reduzido aos identificadores e estados necessários.

O comando deve ser executado diariamente pelo serviço de agendamento do alojamento. A política de cópias de segurança deve garantir que dados eliminados expiram também das cópias segundo o ciclo operacional definido para produção.

## 7. Segurança e privacidade adicionais

- Fotografias têm validação de tipo, extensão e limite de 5 MB.
- Currículos mantêm o limite de 10 MB e o acesso protegido existente.
- As páginas legais são públicas. Pesquisa, perfis, ficheiros e interacções continuam restritos a membros aprovados.
- As mensagens de email não incluem currículos, dados privados da candidatura ou conteúdo integral de contactos.
- Os emails administrativos contêm apenas o nome, o tipo de tarefa e uma ligação autenticada para revisão.
- A configuração de produção documenta SMTP, `PUBLIC_BASE_URL`, `KALITICA_ADMIN_EMAILS`, PostgreSQL, armazenamento de media, cópias de segurança e tarefa diária de eliminação.

## 8. Tratamento de erros

Falhas de validação permanecem junto do campo relevante. Uma candidatura não pode ser submetida com representação incompleta. A autorização pública da organização não pode expor dados se a representação não tiver sido aprovada.

Falhas de email são registadas sem alterar o estado já decidido. Falhas na eliminação de uma conta interrompem apenas essa conta e são reportadas, permitindo que as restantes contas elegíveis sejam processadas.

As páginas legais devolvem estado 200 e têm ligações canónicas. Áreas privadas e ficheiros continuam a devolver redireccionamento ou 404 conforme as regras existentes.

## 9. Testes e aceitação

Os testes automatizados cobrem:

- as três línguas em todos os grupos de páginas
- ausência de texto português fixo nas páginas francesa e inglesa seleccionadas
- taxonomia localizada com alternativa em português
- acesso público às três páginas legais e às respectivas traduções
- criação única dos registos de consentimento
- validação e privacidade dos campos de organização
- publicação opcional do nome e cargo da organização
- emails de submissão e decisão com destinatários e ligações correctos
- falha de email sem reversão de decisões
- agendamento, restauração, simulação e eliminação de contas
- validação de fotografias
- manutenção das regras de acesso à rede e publicação separada do perfil

A aceitação final inclui todos os testes Django, verificação de migrações, `check --deploy`, compilação dos catálogos e revisão manual em computador e telemóvel dos percursos de visitante, candidatura, membro e administração.

## 10. Entrega incremental

O trabalho é dividido em quatro entregas independentes:

1. Documentos legais e consentimentos
2. Representação de organizações
3. Emails operacionais
4. Tradução integral, taxonomia localizada, eliminação e validação final

Cada entrega termina com testes, revisão do diff, commit e push para `main`. Uma falha numa entrega não autoriza a publicação parcial em produção.
