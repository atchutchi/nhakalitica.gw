# Kalitica Audit Remediation Design

Data: 6 de Agosto de 2026

## Objectivo

Corrigir os problemas identificados na auditoria de produção, criar uma área própria de gestão de membros dentro da Administração Kalitica e validar os percursos principais de visitante, membro e administrador antes da apresentação formal da demonstração.

O trabalho preserva a arquitectura Django, o design system Kalitica, o modelo de adesão aprovado e as versões portuguesa, francesa e inglesa. Não altera a decisão de manter o registo público e o envio real de emails desactivados durante a demonstração.

## Decisões aprovadas

- A interface actual mantém a composição, tipografia, cores, espaçamento e componentes do design system Kalitica.
- As correcções são incrementais. Não existe um redesenho geral do site.
- “Membros” passa a abrir uma área própria em `/administracao/membros/`.
- A administração Django deixa de fazer parte do percurso normal da equipa.
- A administração Django continua disponível apenas para superutilizadores através de uma ligação secundária identificada como “Administração técnica”.
- A nova área de membros não permite eliminações, aprovações ou suspensões em massa.
- A recuperação de uma conta só aparece quando a conta está inactiva e ainda se encontra dentro do prazo de recuperação de 30 dias.
- Cada alteração funcional recebe um teste de regressão antes da implementação.
- Cada lote concluído termina com testes, revisão do diff, commit e push para `main`.

## 1. Área própria de membros

### Lista de membros

A rota `/administracao/membros/` usa o mesmo `admin-shell`, a mesma navegação lateral e os mesmos componentes visuais das filas de candidaturas e perfis.

A página apresenta:

- pesquisa por nome e email
- filtro por estado da conta
- filtro por tipo de membro Efectivo ou Observador
- filtro por estado da adesão
- nome e email da conta
- tipo de membro e ligação à Guiné-Bissau
- estado da adesão
- estado de publicação do perfil
- estado da conta, incluindo activa, inactiva ou em recuperação
- ligação para o detalhe do membro

Os filtros têm `label` visível ou uma designação acessível equivalente. O estado activo é mantido na ligação quando a pesquisa é alterada ou paginada.

Em computador, os resultados usam uma tabela ou linhas estruturadas com cabeçalhos claros. Em telemóvel, cada resultado passa para um cartão que mantém a ordem nome, conta, adesão, perfil e acção. Não existe deslocamento horizontal na página.

### Detalhe do membro

A rota `/administracao/membros/<id>/` apresenta apenas informação operacional necessária:

- identidade da conta
- estado activo ou inactivo
- confirmação do email
- datas de desactivação e eliminação agendada quando existirem
- resumo da adesão
- resumo da publicação do perfil
- ligações para rever a candidatura e o perfil

Uma conta activa não apresenta acções de recuperação. Uma conta inactiva dentro do prazo de 30 dias apresenta “Restaurar conta”. A acção exige confirmação explícita, usa `POST`, conserva a protecção CSRF e cria um registo de auditoria. A restauração mantém as regras já aprovadas: reactiva a conta, limpa as datas de eliminação e coloca o perfil em estado privado e não pesquisável.

Uma conta inactiva fora do prazo não apresenta recuperação. O detalhe explica que o prazo terminou e não oferece uma acção que possa falhar ou contradizer a política de retenção.

### Administração técnica

Uma ligação discreta “Administração técnica” aparece apenas para superutilizadores. A ligação abre `/admin/` e é acompanhada por texto que explica que se destina a manutenção avançada. Não substitui as filas operacionais da Administração Kalitica.

## 2. Correcções da experiência pública

### Registo encerrado

A página `/conta/criar/` mantém a composição de autenticação, mas coloca o título “Registos temporariamente encerrados”, a explicação e a acção de entrada dentro do primeiro ecrã. O painel de marca deixa de ocupar sozinho toda a altura antes da mensagem principal.

### Contraste da página inicial

O título “Como funciona a adesão” e as traduções usam uma cor com contraste suficiente sobre o fundo azul. A cor recomendada é branca, tal como o restante conteúdo de destaque do cartão. A alteração aplica-se às três línguas sem duplicar regras.

### Menus móveis

Os menus público e privado actualizam `aria-expanded` e o nome acessível do botão. Quando fechados anunciam “Abrir menu”. Quando abertos anunciam “Fechar menu”. O foco visível usa o turquesa do design system e mantém contraste sobre fundos claros e escuros.

## 3. Correcções da experiência do membro

### Estado do perfil próprio

A pré-visualização deriva a mensagem do estado real de publicação e descoberta. Um perfil aprovado, público e pesquisável não pode mostrar o aviso de que ainda não aparece na pesquisa. Estados em revisão, privados, suspensos ou com alterações pendentes mantêm mensagens próprias e verdadeiras.

### Navegação de definições

A opção activa é calculada por rota. “Editar perfil”, “A minha conta”, “Alterar palavra-passe” e “Privacidade” só ficam activas na página correspondente. A navegação intermédia permite quebra controlada ou deslocamento discreto sem cortar a opção activa nem apresentar uma barra permanente.

### Mensagens vazias

O estado vazio de Mensagens usa os mesmos cartões, sombras e cores das restantes páginas privadas. Inclui uma acção “Pesquisar profissionais” que conduz ao Directório. Não usa o rótulo laranja que diverge da paleta funcional.

### Comparação sem favoritos

“Comparar membros” não aparece como acção disponível quando não existem pelo menos dois favoritos seleccionáveis. O estado vazio explica que o membro deve guardar perfis antes de comparar e oferece uma ligação ao Directório.

### Sugestão de área

A nota na página de Áreas inclui uma ligação de email para `info@nhakalitica.gw`. O texto explica que a sugestão será revista pela equipa e não cria automaticamente uma área pública.

## 4. Correcções da administração

### Navegação e sessão

O cabeçalho administrativo apresenta:

- ligação “Voltar à rede” para o painel do membro
- acção “Sair” através de formulário `POST`
- email da conta actual

A ligação activa da barra lateral recebe uma classe visual e `aria-current="page"`. O comportamento aplica-se a Painel, Candidaturas, Perfis, Membros, Denúncias e Auditoria.

### Filtros

Os selectores de Candidaturas, Perfis, Membros e Denúncias recebem nomes acessíveis específicos. A pesquisa de Auditoria recebe `label` acessível. O envio automático do filtro de candidaturas permanece disponível, mas o controlo continua utilizável com teclado.

### Acções por estado

O detalhe de perfil apresenta apenas transições válidas para o estado actual. Um perfil aprovado não apresenta “Aprovar publicação”. Um perfil suspenso apresenta “Restaurar”. Pedir correcções, recusar e suspender continuam sujeitos às regras de serviço existentes.

As decisões destrutivas ou restritivas mantêm confirmação explícita. Erros de validação aparecem com `role="alert"` e não apagam a nota escrita pelo administrador.

### Auditoria responsiva

Em ecrãs largos, o histórico mantém a tabela. Em ecrãs estreitos, cada evento é apresentado como um bloco legível com Data, Administrador, Acção, Alvo e Contexto. A informação não depende de deslocamento horizontal e a ordem de leitura é mantida.

## 5. Erros e recuperação

São criadas páginas Kalitica para acesso negado e falha de CSRF.

A página 403 explica que a conta não tem permissão para abrir aquela área e oferece uma ligação segura para o painel ou para o início de sessão.

A falha de CSRF explica que o formulário expirou, normalmente depois de uma actualização ou deploy. A página oferece “Actualizar e tentar novamente” e não sugere que a palavra-passe esteja incorrecta.

As páginas não expõem detalhes técnicos, tokens, excepções ou configurações internas.

## 6. Internacionalização

Todo o texto novo usa os mecanismos de tradução do Django. Português é a origem. Francês e inglês recebem traduções completas antes da publicação.

Os catálogos compilados são actualizados no mesmo lote. Não podem existir entradas vazias, provisórias ou marcadas como `fuzzy` para o novo conteúdo.

A administração técnica Django pode manter nomes internos de modelos, mas o percurso normal da Administração Kalitica deve estar integralmente traduzido.

## 7. Acessibilidade

O alvo continua a ser WCAG 2.2 AA para os percursos principais.

As correcções incluem:

- nomes acessíveis para filtros e pesquisas
- `aria-current` na navegação activa
- nomes dinâmicos nos botões dos menus móveis
- foco visível com contraste suficiente
- páginas de erro com título, explicação e recuperação
- estados vazios com acção clara
- ausência de deslocamento horizontal a 320 px
- alvos interactivos com pelo menos 44 px quando o componente permite interacção por toque

A validação manual confirma teclado, ordem de foco, estado expandido, mensagens de erro e leitura estrutural. As capturas visuais não são apresentadas como prova de conformidade integral.

## 8. Testes e validação

### Testes automatizados

Os testes cobrem:

- acesso da nova área de membros apenas por staff
- pesquisa e filtros de membros
- informação e ligações do detalhe
- recuperação permitida e bloqueada conforme o prazo
- registo de auditoria da recuperação
- ausência de acções administrativas inválidas
- navegação activa e saída por `POST`
- nomes acessíveis dos filtros
- mensagens correctas de publicação do perfil
- estados vazios de Mensagens e Favoritos
- páginas 403 e CSRF com recuperação
- traduções das novas mensagens
- manutenção das regras de acesso à rede

Cada correcção começa com um teste que falha pelo motivo esperado. A implementação mínima faz o teste passar antes de qualquer refactorização.

### Validação manual

A validação final percorre:

1. visitante em português, francês e inglês
2. início de sessão e erro de formulário expirado
3. membro aprovado no painel, Directório, perfil, definições, favoritos, mensagens, notificações e áreas
4. administrador no painel, candidaturas, perfis, membros, denúncias e auditoria
5. saída do membro e saída do administrador
6. computador, largura intermédia e telemóvel
7. teclado, foco, nomes acessíveis e ausência de deslocamento horizontal

Cada etapa recebe uma captura aceite ou um bloqueio identificado. As capturas são guardadas no relatório de auditoria e inspeccionadas antes da entrega.

## 9. Publicação e aceitação

O trabalho é dividido em lotes pequenos:

1. erros públicos e navegação móvel
2. perfil, definições e estados vazios do membro
3. administração e nova área de membros
4. traduções e validação integral

Cada lote termina com testes relevantes, `manage.py check`, revisão do diff, commit e push. Depois do último deploy, o estado do Railway deve ser `success` e os percursos principais são repetidos no endereço de produção.

A entrega é aceite quando os problemas 1 a 16 do relatório estão corrigidos ou documentados com uma limitação aprovada, os testes completos passam e a validação final não encontra bloqueios críticos ou altos.

## Fora do âmbito

Este trabalho não activa pagamentos, registos públicos, SMTP real, vagas, contas empresariais autónomas, equipas de recrutamento, facturação ou migração para a PTisp. Também não elimina os perfis de demonstração nem substitui a revisão jurídica final necessária antes da abertura pública.
