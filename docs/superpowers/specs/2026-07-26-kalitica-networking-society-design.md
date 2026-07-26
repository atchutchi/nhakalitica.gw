# Kalitica Networking Society

Data: 26 de Julho de 2026

Estado: aprovado para planeamento

## Objectivo

Criar no repositório `atchutchi/nhakalitica.gw` uma aplicação Django independente, derivada funcionalmente do CVLink e redesenhada de acordo com a identidade Kalitica. A plataforma serve como rede profissional privada para a Guiné-Bissau, a diáspora guineense e profissionais com ligação relevante ao país.

Os quatro painéis em `output/mockups` são a referência visual obrigatória:

1. `01-paginas-publicas-e-autenticacao.png`
2. `02-adesao-e-aprovacao.png`
3. `03-rede-profissional-privada.png`
4. `04-conta-privacidade-e-administracao.png`

## Limites do lançamento

Incluído:

- Página pública institucional.
- Registo, confirmação de email, login e recuperação de palavra-passe.
- Interface em português, francês e inglês.
- Candidatura a membro Efectivo ou Observador.
- Elegibilidade por cidadania guineense, ascendência na diáspora ou ligação relevante à Guiné-Bissau.
- Aprovação manual para os dois tipos de membro.
- Perfil profissional com revisão e publicação separadas da adesão.
- Directório privado, pesquisa, filtros, áreas, favoritos, comparação e contacto protegido.
- Conta, privacidade, notificações, moderação, suspensões e auditoria.

Excluído:

- Cobrança, subscrições, quotas e pagamentos.
- Contas autónomas de empresas.
- Tradução automática do conteúdo escrito pelos membros.
- Directório ou perfis acessíveis sem aprovação.
- Publicação de vagas e planos comerciais.

## Arquitectura

A aplicação mantém Django como plataforma principal e reutiliza a arquitectura funcional do CVLink. Os módulos são independentes e comunicam através de modelos e serviços com responsabilidades delimitadas.

`accounts` gere identidade, email, autenticação, recuperação, preferência de idioma e desactivação.

`memberships` gere tipo de membro, relação com a Guiné-Bissau, motivação, candidatura, estados, decisões e suspensão.

`profiles` gere identidade profissional, experiência, formação, competências, idiomas, currículo, privacidade, revisão e publicação.

`taxonomy` gere sectores, áreas, especializações, competências e opções de pesquisa adaptadas à realidade guineense.

`interactions` gere favoritos, comparação, listas privadas, pedidos de contacto e notificações.

`moderation` gere filas de candidatura, filas de publicação, denúncias, suspensão e auditoria.

`core` gere página pública, páginas institucionais, selector de idioma, saúde, SEO público e bloqueio de rotas privadas.

## Modelo de acesso

1. Um visitante consulta páginas institucionais e cria conta.
2. A confirmação de email permite login na área de candidatura.
3. Antes da aprovação, o utilizador só acede à candidatura, conta, ajuda e correcções pedidas.
4. A adesão aprovada abre a rede privada.
5. A publicação do perfil exige adesão aprovada, perfil completo e revisão de publicação aprovada.
6. Um membro aprovado pode manter o perfil oculto por escolha própria.
7. Uma suspensão bloqueia a rede e oculta o perfil sem eliminar dados.
8. Efectivos e Observadores têm os mesmos direitos na rede profissional. A diferença é apenas associativa.
9. Um representante de organização usa uma conta individual e passa pelo mesmo processo.

## Estados de adesão

- Rascunho
- Submetida
- Em análise
- Correcções necessárias
- Aprovada
- Recusada
- Suspensa

Cada decisão administrativa guarda revisor, data, estado anterior, estado novo e nota interna. A recusa, suspensão e pedido de correcções exigem justificação.

## Estados de publicação do perfil

- Privado
- Incompleto
- Pronto para revisão
- Em revisão
- Correcções necessárias
- Publicado
- Oculto pelo membro
- Oculto por suspensão

A decisão de adesão nunca publica automaticamente o perfil.

## Páginas públicas e autenticação

- Página inicial
- Sobre a Kalitica e missão
- Tipos de adesão
- Como funciona
- Contacto e ajuda
- Política de privacidade e termos
- Registo
- Confirmação e reenvio de email
- Login
- Recuperação e alteração de palavra-passe

A página inicial apresenta o posicionamento, a natureza privada, a elegibilidade e a acção Pedir adesão. Não apresenta números fictícios, perfis reais ou preços.

## Candidatura

O painel mostra uma lista de passos e progresso real. A candidatura recolhe tipo de adesão, relação com a Guiné-Bissau, justificação, dados essenciais, perfil profissional inicial, consentimentos e revisão final.

O utilizador pode guardar rascunhos. Depois de submeter, os campos ficam bloqueados, excepto quando a equipa pede correcções. As notificações explicam o que mudou e qual é a próxima acção.

## Rede privada

O painel do membro mostra conclusão do perfil, visibilidade, notificações e actividade relevante. Não utiliza métricas inventadas.

A pesquisa suporta profissão, competências, sector, área, localização, disponibilidade, idiomas, tipo de membro e relação com a Guiné-Bissau. Os resultados mostram apenas informação autorizada pelo membro.

O perfil apresenta experiência, formação, competências, idiomas, localização permitida, currículo quando partilhável e acção de contacto protegido.

Favoritos, comparação e notas são privados para o membro que os criou. Um pedido de contacto não revela email ou telefone antes da aceitação e das regras de visibilidade aplicáveis.

## Administração

O painel administrativo separa candidaturas de adesão e publicação de perfis. Cada fila suporta filtros, histórico, notas internas e decisões com confirmação.

As permissões distinguem administradores gerais, revisores de adesão e moderadores de perfil quando necessário. O histórico de auditoria não é editável pela interface.

## Internacionalização

O português é o idioma de origem. Francês e inglês cobrem navegação, formulários, validação, mensagens, emails e páginas públicas. A preferência é guardada por conta e pode ser alterada a qualquer momento.

Os textos escritos pelos membros mantêm o idioma original. O layout deve suportar expansão de texto de pelo menos 30 por cento sem corte, sobreposição ou truncagem inadequada.

## Privacidade e segurança

- A rede é privada e exige adesão aprovada.
- Contacto, localização detalhada, email, telefone e currículo têm controlos separados.
- Acesso negado não deve confirmar a existência de perfis privados.
- Ficheiros de currículo exigem validação de tipo e tamanho.
- Login e recuperação têm limitação de tentativas.
- Alterações sensíveis e decisões administrativas entram em auditoria.
- Suspensão e desactivação preservam dados conforme as regras de retenção.
- Produção exige HTTPS, cookies seguros, HSTS, chave secreta externa e configuração explícita de origens.

## Erros e estados vazios

Cada formulário apresenta resumo e erros junto aos campos. O texto indica o problema e a correcção possível. Dados já introduzidos são preservados após erro.

Listas vazias ensinam a próxima acção. Pesquisa sem resultados permite limpar filtros. Falha de email permite reenvio. Sessão expirada devolve ao login e preserva o destino seguro. Falhas administrativas não deixam decisões parciais.

## Design e responsividade

`PRODUCT.md` e `DESIGN.md` são normativos. Os quatro painéis aprovados definem composição, hierarquia, densidade, navegação, paleta e componentes.

Desktop usa conteúdo até 1280px, filtros laterais na pesquisa e navegação lateral na administração. Tablet reorganiza colunas e preserva acções. Mobile começa em 320px, converte filtros em painel acessível, empilha formulários e mantém acções críticas visíveis.

Nenhuma página pode apresentar deslocamento horizontal. Todos os controlos interactivos têm foco visível, estados de hover, active, disabled, loading, error e success quando aplicáveis.

## Dados iniciais

A taxonomia inicial deve ser adaptada à Guiné-Bissau e revista antes de ser tratada como definitiva. Dados de demonstração só podem existir no ambiente de desenvolvimento e devem estar claramente identificados. Produção começa sem membros, métricas ou actividade fictícia.

## Estratégia de testes

- Testes de modelos, permissões, transições de estado e auditoria.
- Testes de registo, confirmação de email, login e recuperação.
- Testes de isolamento entre candidato, membro aprovado, membro suspenso, revisor e administrador.
- Testes de publicação independente da adesão.
- Testes de privacidade de cada campo e currículo.
- Testes de pesquisa e filtros com dados autorizados.
- Testes de pedidos de contacto, favoritos, comparação e notificações.
- Testes de internacionalização e mensagens nos três idiomas.
- Testes de acessibilidade automatizados e navegação por teclado.
- Testes visuais em desktop, tablet e mobile contra os painéis aprovados.
- Verificação de produção com `manage.py check --deploy` e configuração sem segredos no repositório.

## Critérios de aceitação

1. A aplicação mantém todas as funcionalidades aprovadas do CVLink que pertencem ao lançamento.
2. Nenhum visitante ou candidato não aprovado acede ao directório ou a perfis.
3. Efectivo e Observador têm o mesmo acesso profissional.
4. Adesão e publicação de perfil têm fluxos e decisões independentes.
5. As quatro famílias de páginas correspondem visualmente aos painéis aprovados.
6. Português, francês e inglês funcionam em interface, validações e emails.
7. Privacidade, suspensão e auditoria são verificadas por testes.
8. O site funciona a partir de 320px, por teclado e com contraste WCAG AA.
9. A suite de testes, verificações Django e revisão visual passam antes de cada push relevante.
10. O repositório `atchutchi/nhakalitica.gw` recebe commits pequenos, coerentes e enviados para `main` conforme o avanço aprovado.
